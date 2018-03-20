import sys
import scrapy as spy

class DoctIRSpyder(spy.Spyder):
    name = 'symptomScraper'
    domainFilename = sys.argv[1]

    with open(domainFilename, 'r') as domFile:
        allowed_domains = domFile.read().split()




def main():
    return



if __name__ == '__main__':
    main()