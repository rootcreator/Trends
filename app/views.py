import requests
from django.shortcuts import render, redirect
from googleapiclient.discovery import build

from .models import Trend


def set_region(request):
    region = request.GET.get('region', 'US')
    request.session['region'] = region
    return redirect('index')


def index(request):
    region = request.session.get('region', 'US')
    trends = Trend.objects.all()
    youtube_trends = fetch_youtube_trends(region=region)
    twitter_trends = fetch_twitter_trends()
    reddit_trends = fetch_reddit_trends()
    return render(request, 'index.html', {
        'trends': trends,
        'youtube_trends': youtube_trends,
        'twitter_trends': twitter_trends,
        'reddit_trends': reddit_trends,
        'selected_region': region
    })


def search_trends(request):
    query = request.GET.get('q')
    region = request.session.get('region', 'US')
    if query:
        youtube_trends = fetch_youtube_trends(query, region)
        reddit_trends = fetch_reddit_trends(query)
        twitter_trends = fetch_twitter_trends(query)
        results = youtube_trends + reddit_trends + twitter_trends
        return render(request, 'search_results.html', {
            'results': results,
            'query': query,
            'region': region
        })
    return redirect('index')


def fetch_twitter_trends(query=None):
    url = "https://twitter154.p.rapidapi.com/trends/"
    headers = {
        "x-rapidapi-key": "1ecad14232mshea32a62c1e4dc2ap181062jsn38bf6995676a",
        "x-rapidapi-host": "twitter154.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        trends_data = response.json()
        formatted_trends = []
        for trend_data in trends_data:
            trends = trend_data.get('trends', [])
            formatted_trends.extend([{
                'title': trend['name'],
                'description': '',
                'url': trend.get('url', ''),
                'source': 'Twitter',
                'cover_picture_url': ''
            } for trend in trends])

        if query:
            formatted_trends = [trend for trend in formatted_trends if query.lower() in trend['title'].lower()]

        return formatted_trends

    return []


def fetch_reddit_trends(query=None):
    url = "https://www.reddit.com/r/all/hot.json"
    headers = {'User-agent': 'Trend Finder Bot'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json().get('data', {}).get('children', [])
        trends = [{
            'title': trend['data']['title'],
            'description': trend['data'].get('selftext', ''),
            'url': f"https://www.reddit.com{trend['data']['permalink']}",
            'source': 'Reddit',
            'cover_picture_url': ''
        } for trend in data]

        if query:
            trends = [trend for trend in trends if query.lower() in trend['title'].lower()]

        return trends

    return []


YOUTUBE_API_KEY = 'AIzaSyAf63RX80yCepWkqTCbOJqH9NwU3n_ttpg'


def fetch_youtube_trends(query=None, region='US'):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        chart="mostPopular",
        regionCode=region,
        maxResults=21
    )
    response = request.execute()
    if 'items' in response:
        videos = response['items']
        formatted_videos = []
        for video in videos:
            title = video['snippet']['title']
            description = video['snippet'].get('description', '')
            video_url = f"https://www.youtube.com/watch?v={video['id']}"
            cover_picture_url = video['snippet']['thumbnails']['high']['url']
            formatted_videos.append({
                'title': title,
                'description': description,
                'url': video_url,
                'source': 'YouTube',
                'video_url': video_url,
                'cover_picture_url': cover_picture_url,
            })

        if query:
            formatted_videos = [video for video in formatted_videos if query.lower() in video['title'].lower()]

        return formatted_videos

    return []


def search_trending_data(query):
    twitter_results = fetch_twitter_trends(query)
    reddit_results = fetch_reddit_trends(query)
    youtube_results = fetch_youtube_trends(query)
    return twitter_results + reddit_results + youtube_results


def update_trends(request):
    data = fetch_trending_data()
    for item in data:
        Trend.objects.update_or_create(
            title=item['title'],
            defaults={'description': item['description'], 'url': item['url'], 'source': item['source']}
        )
    return redirect('index')


def fetch_trending_data(region='US'):
    twitter_trends = fetch_twitter_trends()
    reddit_trends = fetch_reddit_trends()
    youtube_trends = fetch_youtube_trends(region=region)
    return twitter_trends + reddit_trends + youtube_trends
