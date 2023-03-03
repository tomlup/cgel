from depedit import DepEdit
import conllu
from conllu import TokenList, TokenTree, Token
from typing import List

from collections import defaultdict
import constituent
import copy
from tqdm import tqdm
import random
import glob
from cgel import Tree

def token_tree_to_list(tree: TokenTree) -> TokenList:
    def flatten_tree(root_token: TokenTree, token_list: List[Token] = []) -> List[Token]:
        token_list.append(root_token.token)

        for child_token in root_token.children:
            flatten_tree(child_token, token_list)

        return token_list

    tokens = flatten_tree(tree)
    token_list = TokenList(tokens, tree.metadata)
    return token_list

test = False

def combine_conllus():
    with open('conversions/all.conllu', 'w') as fout:
        for file in glob.glob('datasets/*.conllu'):
            with open(file) as fin:
                for line in fin:
                    fout.write(line)

def convert(infile: str, resfile: str, outfile: str):
    """Convert a UD treebank to CGEL.
    
    Args:
        infile: UD source file in CONLLU format.
        resfile: Logging file for results.
        outfile: Output file for the converted CGEL treebank.
    """

    print('Getting files...')
    infile = open(infile)
    config_file = open("convertor/ud-to-cgel.ini")
    d = DepEdit(config_file)

    print('Running depedit...')
    result = d.run_depedit(infile)

    print('Done with depedit.')
    types = defaultdict(int)
    pos = defaultdict(int)

    sent = [0, 0, 0]
    tok = [0, 0]

    # create projected constituents recursively
    def project_categories(node):
        if test:
            print(node.token['form'])
        upos, form, deprel = node.token['upos'], node.token['form'], node.token['deprel']

        if deprel == 'Clause':
            rel, pos = 'Root', 'Clause'
        elif ':' in deprel:
            rel, pos = deprel.split(':')
        else:
            rel, pos = deprel, upos

        # collect all the new projected categories for reference
        projected = {}

        # keep track of child to control
        last = node
        orig_node = copy.deepcopy(node)
        status = True
        if upos in constituent.projections:

            # go through all projected categories
            if upos != pos:
                for r, level in enumerate(constituent.projections[upos]):

                    # make new node
                    head = copy.deepcopy(orig_node)
                    head.token['form'] = '_'
                    head.token['upos'] = level
                    head.token['deprel'] = f'{rel}:{level}'
                    head.children = [last]
                    projected[level] = head

                    # deprel of child node must be Head
                    last.token['deprel'] = last.token['deprel'].replace(f'{rel}:', 'Head:')
                    last.token['head'] = head.token['id']
                    last = head


                    # if we reach last projected category, break
                    # its pos is simply what we stored in upos!
                    if level == pos:
                        node.token['deprel'] = node.token['deprel'].replace(f':{pos}', f':{upos}')
                        break

        
            remaining = []
            for i, child in enumerate(node.children):
                rel = child.token['deprel'].split(':')[0]
                level = constituent.level.get((rel, upos), None)
                result, status2 = project_categories(child)
                status = status and status2
                if level and level in projected:
                    projected[level].children.append(result)
                    projected[level].children.sort(key=lambda x: x.token['id'])
                else:
                    remaining.append(result)
                
            last.children.extend(remaining)
            last.children.sort(key=lambda x: x.token['id'])
            node.children = []
        else:
            status = False
            for i, child in enumerate(node.children):
                node.children[i], _ = project_categories(child)

        return last, status

    # convert to constituency and write out CGEL trees
    print('Converting to constituency...')
    with open(outfile + '.cgel', 'w') as fout:

        # get flattened CGEL trees (post-conversion)
        trees = conllu.parse(result)

        for i, sentence in enumerate(trees):

            # create the tree, project unary nodes
            tree = sentence.to_tree()
            fixed, status = project_categories(tree)

            # convert to tokenlist, make cgel object
            orig = token_tree_to_list(fixed)
            converted = Tree()
            converted.metadata = sentence.metadata
            converted.sentnum = converted.metadata['sent_num'] = i + 1
            converted.sent = converted.metadata['sent'] = ' '.join([str(token) for token in sentence])

            keys = list(converted.metadata)
            for key in keys:
                if ' ' in key:
                    del converted.metadata[key]
            if 'sentid' not in converted.metadata:
                converted.metadata['sent_id'] = converted.sentnum
                converted.sentid = converted.sentnum
            if 'text' not in converted.metadata:
                converted.metadata['text'] = converted.sent
                converted.text = converted.sent

            # get id to j mapping
            # unary nodes have same id so have to deal with that (only first is headable--not perfect)
            mapping = {0: -1}
            last = -1
            for j, word in enumerate(orig):
                if not isinstance(word['id'], int): continue
                if word['id'] not in mapping:
                    mapping[word['id']] = j
                last = word['id']

            # go through tokens and add to cgel
            last = -1
            complete = True
            for j, word in enumerate(orig):
                if not isinstance(word['id'], int): continue
                # add token
                head = j-1 if word['id'] == last else mapping[word['head']]
                deprel: str = word['deprel'].split(':')[0]
                converted.add_token(
                    token=None,
                    deprel=deprel if deprel != 'Root' else None,
                    constituent=word['upos'],
                    i=j,
                    head=head
                )

                # stats
                pos[word['upos']] += 1
                types[deprel] += 1
                if deprel.islower(): complete = False
                else: tok[0] += 1
                tok[1] += 1
                
                # add text if it is there
                if word['form'] != "_":
                    converted.add_token(
                        token=word['form'],
                        deprel=None,
                        constituent=None,
                        i=j,
                        head=j
                    )

                # update last
                last = word['id']
            
            # output
            fout.write(converted.draw(include_metadata=True) + '\n\n')
            sent[1] += 1
            if complete: sent[0] += 1

    with open(resfile, 'w') as fout:
        fout.write(f'{sent[0]} / {sent[1]} sentences fully parsed ({sent[0] * 100 / sent[1]:.2f}%).\n')
        fout.write(f'{sent[2]} / {sent[1]} sentences with all projections known ({sent[2] * 100 / sent[1]:.2f}%).\n')
        fout.write(f'{tok[0]} / {tok[1]} words fully parsed ({tok[0] * 100 / tok[1]:.2f}%).\n\n')
        fout.write('POS\n')
        for i in pos:
            fout.write(f'{i}, {pos[i]}\n')
        fout.write('\nDEP\n')
        for i in types:
            if i[1].islower(): fout.write('-->')
            fout.write(f'{i}, {types[i]}\n')

    with open(outfile + '.conllu', 'w') as fout:
        fout.write(result)

def main():
    # combine_conllus()
    # convert('conversions/all.conllu', 'conversions/results.txt', 'conversions/ewt_auto')
    convert('datasets/ewt_ud.conllu', 'conversions/ewt_results.txt', 'conversions/ewt_pred')
    convert('datasets/twitter_ud.conllu', 'conversions/twitter_results.txt', 'conversions/twitter_pred')

if __name__ == '__main__':
    main()