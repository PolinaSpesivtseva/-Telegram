from telethon.tl import types
import logging
import asyncio
from typing import List, Optional
from itertools import islice


logger = logging.getLogger(__name__)

async def get_info_from_message(
    client,
    message, 
    channel, 
    key_words=[], 
    stop_words=[], 
    is_need_comments=True,
    limit_comments=1000,
    is_need_reactions=True
):
    """Filter and format post

    :param message: (object) message recieved from Telegram
    :param channel: (str) channel username
    :param stop_words: (list) stop words
    :param key_words: (list) strong key words
    :param to_date: (int) Unix Timestamp
    :param from_date: (int) Unix Timestamp
    :param is_need_comments: (bool)

    :return post: (dict) filtered and formatted post
    """

    if message.message:
        post = {}
        post['id'] = message.id
        post["channel_id"] = message.to_id.channel_id
        post["channel"] = channel
        post['date'] = int(message.date.timestamp())
        post['text'] = message.message
        post['views'] = message.views
        post['id_owner'] = message.to_id.channel_id
        post['url'] = 'https://t.me/' + channel + '/' + str(message.id)
        post['avatar'] = ''
        post['text_length'] = len(message.message)
        post['reposts_count'] = message.forwards
        post['comments_count'] = 0
        post['comments'] = []
        post['reactions'] = []

        # Проверка на кейворды и стоп ворды
        key_words = [kw.lower() for kw in key_words]
        stop_words = [kw.lower() for kw in stop_words]
        text = message.message.lower()
        for keyword in key_words:
            if keyword in text:
                for sw in stop_words:
                    if sw in text:
                        return 
            else:
                return 

        #####################################
        ###### пометка forward откуда #######
        fwd_from = None
        fwd_from_channel_title = None
        # Check if the message was forwarded
        if message.forward:
        # If the message was forwarded, print the original channel name or ID
        # Note: Depending on the forward privacy settings, you might get an ID or a username
            fwd_from = message.forward.chat if message.forward.chat else message.forward.channel_id
            if isinstance(fwd_from, types.Channel):
                fwd_from_channel_title = fwd_from.title
            else:
                fwd_from_channel_title = "Unknown Channel"
        post["fwd_from"] = fwd_from_channel_title
            
        if is_need_comments and limit_comments > 0:
            try:
                async for comment in client.iter_messages(entity=channel, reply_to=message.id, reverse=True):
                    limit_comments -= 1
                    post['comments_count'] += 1
                    if comment.message:
                        comment_processed = {
                            'id': f"{comment.id}_{message.id}_{message.to_id.channel_id}",
                            'owner_id': comment.sender_id,
                            'comment_id': comment.id,
                            'owner': f"{comment.sender.username}",
                            'date': int(comment.date.timestamp()),
                            'text': comment.message,
                            "reactions": [],
                        }

                        # limit for comment reactions
                        limit = 10
                        # print("bebebeb", comment.reactions.results[1].to_dict())

                        if comment.reactions:
                            for r in comment.reactions.results[:limit]:
                                r = r.to_dict()
                                emoji = r["reaction"].get("emoticon", None)
                                if emoji is not None:
                                    comment_processed['reactions'].append({"emoji": emoji, "count": r["count"]})
                                else:
                                    comment_processed['reactions'].append({"document_id": r["reaction"].get("document_id", None), "count": r["count"]})

                        post['comments'].append(comment_processed)
                    if limit_comments == 0:
                        break
            except:
                pass
        
        if is_need_reactions:
            if message.reactions:
                for r in message.reactions.to_dict()["results"]:
                    emoji = r["reaction"].get("emoticon", None)
                    if emoji is not None:
                        post['reactions'].append({"emoji": emoji, "count": r["count"]})
                    else:
                        post['reactions'].append({"document_id": r["reaction"].get("document_id", None), "count": r["count"]})

        return post
    else:
        return


async def async_get_posts(
    client,
    channel,
    key_words : List[Optional[str]]  = [],
    stop_words : List[Optional[str]] = [],
    from_date=None,
    to_date=None,
    is_need_comments=True,
    limit_comments=1000,
    is_need_reactions=True,
    channel_id=None,
):
    """Return list of posts from the given channels
    according to the given search query

    Arguments:

    data = {
    "key_words": |list of strings|,
    "stop_words": |list of strings|,
    "strong_key_words": |list of strings|,
    "origin_key_words": |list of strings|,
    "from_date": |Unix Timestamp|,
    "to_date": |Unix Timestamp|,
    "ids": |list of strings|,
    "is_need_comments" : [0/1] - replies inclusion flag,
    }

    Return:
    
    list of posts = [post1, post2, ...]
    
    where    
    post = {
        'id': (int) unique ID for DB,
        'owner': (str) author's name,
        'id_owner': (int) author's ID,
        'avatar': (str) author's profile pic url,
        'url': (str) post's url,
        'post_id': (int) post unique ID,
        'date': (int) Unix Timestamp post creation time,
        'text': (str) post text,
        'text_length': (int) length of post's text,
        'likes_count': 0,
        'views_count': (int) count of views,
        'reposts_count': 0,
        'comments_count': 0,
        'comments': []  
    }
    """

    async for message in client.iter_messages(
        entity=channel, 
        offset_date=from_date,
        reverse=True,
    ):
        # проверка на выход за время поиска
        if (to_date is not None) and (int(message.date.timestamp()) >= to_date):
            logger.info(f"Достигнут конец итерации для {channel} на timestamp: {message.date.timestamp()}")
            break

        # иначе парсим пост 
        post = await get_info_from_message(
            client, 
            message, 
            channel, 
            key_words, 
            stop_words, 
            is_need_comments=is_need_comments, 
            limit_comments=limit_comments,
            is_need_reactions=is_need_reactions,
        )
        if post is not None:
            post["tg_channel_id"] = channel_id
            yield post

def get_channels_avatar(ids):
    """Parse channels' avatar from telegram site

    :param ids: (list) channels' username

    :return avatars: (dict) channels' avatar url
    """ 
    avatars = {}
    for channel in ids:
        try:
            r = requests.get(f"https://t.me/{channel['username']}")
            soup = BeautifulSoup(r.text, 'lxml')
            avatar = soup.find('img')
            avatars[str(channel['_id'])[4:]] = avatar['src']
        except Exception as err:
            print(err)
    return avatars

def fill_post_owner_and_ava(posts, channels_name, channels_avatar):
    """Fill posts with channel name and avatar

    :param posts: (list) filtered and formatted posts
    :param channels_name: (list) channels info
    :param channels_avatar: (dict) channels avatar url

    :return new_posts: (list) posts with channel name and avatar url
    """
    new_posts = []
    for post in posts:
        for channel in channels_name:
            if str(post['id_owner']) == str(channel['_id'])[4:]:
                post['owner'] = channel['name']
        if channels_avatar.get(str(post['id_owner'])):
            post['avatar'] = channels_avatar[str(post['id_owner'])]
        new_posts.append(post)
    return new_posts