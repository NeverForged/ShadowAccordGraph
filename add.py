import sys
import os

def main():
    '''
    Add to a file...
    '''
    with open('data/character_edges.csv', 'a') as f:
        for i, item in enumerate(sys.argv):
            if i >= 2:
                line = "{},{}\n".format(sys.argv[1], sys.argv[i])
                f.write(line)
                print line



if __name__ == '__main__':
    if len(sys.argv) >=2:
        main()
    else:
        print "Need at least two names"
