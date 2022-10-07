from youtube_search import YoutubeSearch

def searcher(row):
    res = YoutubeSearch(row, max_results=10).to_dict()
    return res