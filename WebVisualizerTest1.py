import httplib2
from bs4 import BeautifulSoup, SoupStrainer
from graphviz import Digraph, Graph, Source
import os
import urllib.request as urllib2
from urllib.parse import urljoin
import gc

#dot = Digraph(comment = 'The Round Table')
#dot.node('A', 'King Arthur')
#dot.node('B', 'Sir Bedevere the Wise')
#dot.node('L', 'Sir Lancelot the Brave')

#dot.edges(['AB', 'AL'])
#dot.edge('B', 'L', constaint = 'false')

#http = httplib2.Http()
#status, response = http.request('http://www.nytimes.com')

#dot.render('test-output/round-table.gv', view=True)

#for link in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
#    if link.has_attr('href'):
#        print (link['href'])

styles = {
    'graph': {
        'fontsize': '16',
        'fontcolor': 'white',
        'bgcolor': '#333333',
        'rankdir': 'BT',
    },
    'nodes': {
        'fontname': 'Helvetica',
        'shape': 'hexagon',
        'fontcolor': 'white',
        'color': 'white',
        'style': 'filled',
        'fillcolor': '#006699',
    },
    'edges': {
        'style': 'dashed',
        'color': 'white',
        'arrowhead': 'open',
        'fontname': 'Courier',
        'fontsize': '12',
        'fontcolor': 'white',
    }
}


titles = {}

def main(restricted = False):
    global styles
    #gc.set_debug(gc.DEBUG_LEAK)
    
    site = input("What site to crawl?")
    maxDepth = int(input("Max depth?"))
    http = httplib2.Http()
    links = set()
    pages = set()
    #dot = Digraph(comment = site, format="png")
    dot = Graph(comment = site, format="png", engine="sfdp")
    dot.overlap = "true"
    #dot.graph_attr.update(size = "10000000,10000000")

    try:
        soup = BeautifulSoup(urllib2.urlopen(site), "html.parser")
        pageTitle = soup.title.string
        pages.add(pageTitle)
        titles[site] = pageTitle
        soup.decompose()
    except Exception as e:
        pageTitle = site
        print("Error: {0}".format(e))

    siteBase = ""
    try:
        pos1 = site.find(".")
        pos2 = site.find(".", pos1 + 1)
        siteBase = site[pos1+1:pos2]
    except Exception as e:
        print("Error: {0}".format(e))
    print (siteBase)
        
    crawlPage(site, pageTitle, maxDepth, pages, links, restricted, siteBase)
    #print(pages)
    #print(links)

    #for p in pages:
        #print("Adding node: " + p)
        #dot.node(p)
    for l in links:
        try:
            #print("Adding edge: " + l[0] + " -> " + l[1])
            dot.edge(l[0], l[1])
        except Exception as e:
            print("Error: {0}".format(e))

    #print(dot)
    #dot = apply_styles(dot, styles)
    loc = str(dot).find("{")+1
    dot = Source(str(dot)[0:loc] + "\n\tgraph [overlap = prism]\n" + str(dot)[loc:], format="png", engine="sfdp")

    #print("-------------------")

    filename = r'C:\Users\Gabe\Miniconda3\MyScripts\test-crawler15'
    
    dot.save()
    try:
        os.remove(filename)
    except Exception as e:
        print("Error: {0}".format(e))

    try:
        outFile = open(filename + ".txt", "w")
        outFile.write(str(dot))
        outFile.close()
    except Exception as e:
        print("Error: {0}".format(e))
    
    dot.render(filename, view=True)


def crawlPage(site, title, maxDepth, pages, links, restricted = False, siteBase = ""):
    global titles
    
    try:
        print("Crawling " + site + ", with maxDepth = " + str(maxDepth))
        http = httplib2.Http()
        status, response = http.request(site)

        soupPage = BeautifulSoup(response, "html.parser", parse_only=SoupStrainer('a'))
        for link in soupPage:
            if link.has_attr('href'):
                linkedPage = link['href']
                linkedPage = urljoin(site, linkedPage)
                print("Getting title for " + linkedPage)
                
                try:
                    if not linkedPage in titles:
                        soup = BeautifulSoup(urllib2.urlopen(linkedPage), "html.parser")
                        linkTitle = soup.title.string
                        soup.decompose()
                        #titles[linkedPage] = linkTitle
                        
                    else:
                        linkTitle = titles[linkedPage]

                    links.add((title, linkTitle))
                    if not linkTitle in pages and not "youtube" in linkedPage and not (restricted and not siteBase in linkedPage):
                        pages.add(linkTitle)
                        if (maxDepth > 1):
                            crawlPage(linkedPage, linkTitle, maxDepth-1, pages, links, restricted, siteBase)

                except Exception as e:
                    print("Error parsing " + linkedPage + "! {0}".format(e))
                    links.add((title, linkedPage[linkedPage.find("http:\\")+7:]))
                    if not linkedPage[linkedPage.find("http:\\")+7:] in pages and not (restricted and not siteBase in linkedPage):
                        pages.add(linkedPage[linkedPage.find("http:\\")+7:])
                        if (maxDepth > 1):
                            crawlPage(linkedPage, linkTitle, maxDepth-1, pages, links, restricted, siteBase)

                #pages.add(linkedPage)
        soupPage.decompose()
    except Exception as e:
        print ("Error on site " + site + ": {0}".format(e))
    gc.collect()

def getTitles(s):
    returnSet = set()
    for pair in s:
        try:
            soup = BeautifulSoup(urllib2.urlopen(pair[0]), "html.parser")
            linkTitle1 = soup.title.string
        except:
            linkTitle1 = pair[0]
            
        try:
            soup = BeautifulSoup(urllib2.urlopen(pair[1]), "html.parser")
            linkTitle2 = soup.title.string
        except:
            linkTitle2 = pair[1]
        returnSet.add((linkTitle1, linkTitle2))
    return returnSet

def crawl(restricted = False):
    main(restricted)

def apply_styles(graph, styles):
    graph.graph_attr.update(
        ('graph' in styles and styles['graph']) or {}
    )
    graph.node_attr.update(
        ('nodes' in styles and styles['nodes']) or {}
    )
    graph.edge_attr.update(
        ('edges' in styles and styles['edges']) or {}
    )
    return graph

    

#main()









