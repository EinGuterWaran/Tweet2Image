import os
import random
import shutil
import urllib.request

import cv2
import pandas as pd
import requests
from PIL import Image, ImageDraw, ImageOps, ImageFont
from pilmoji import Pilmoji

import fetch_tweets as ft

color_codes = [[251, 57, 88], [255, 200, 56], [109, 201, 147], [69, 142, 255],
               [18, 86, 136]]


def circle_image(im):
    size = im.size
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output


def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()
    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent
    return (text_width, text_height)


def tweets_to_images(file, handle, name, showFavsRt, show_date):
    # let name empty for original name
    tweets = pd.read_csv(file)
    profile_image = ft.get_profile_image(handle)
    if name == "":
        name = ft.get_name(handle)
    color2 = color_codes[random.randint(0, len(color_codes) - 1)]
    for ind in tweets.index:
        tweet = tweets['tweet'][ind]
        favs = tweets['favs'][ind]
        retweets = tweets['retweets'][ind]
        tweet_timestamp = tweets['date'][ind]
        tweet_id = tweets['id'][ind]
        media_url = tweets['media_url'][ind]
        color = color_codes[random.randint(0, len(color_codes) - 1)]
        while color2 == color:
            color = color_codes[random.randint(0, len(color_codes) - 1)]
        color2 = color
        tweet_to_image(name, handle, showFavsRt, show_date, tweet,
                       tweet_timestamp, favs, retweets, profile_image,
                       tweet_id, media_url, color[0], color[1], color[2])
    folder = 'cache/'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def tweet_in_lines(tweet, tweet_lines, tw_font):
    tweet = tweet.replace("\n", " \n ")
    tweet_words = tweet.split(" ")
    current_line = ""
    for word in tweet_words:
        if word == "":
            word = ""
        if word == "\n":
            tweet_lines.append(current_line)
            current_line = ""
            continue
        if word.startswith("https://t.co"): continue
        if current_line != "":
            filler = " "
        else:
            filler = ""
        if current_line != "" and word != "" and get_text_dimensions(
                current_line + filler + word, tw_font)[0] > 900:
            tweet_lines.append(current_line)
            current_line = word
        else:
            current_line += filler + word
    if len(current_line) > 0:
        tweet_lines.append(current_line)
    return len(tweet_lines)


def tweet_to_image(name, username, showFavsRt, show_date, tweet,
                   tweet_timestamp, favs, retweets, profile_image, tweet_id,
                   media_url, r, g, b):
    tw_font = ImageFont.truetype("fonts/HelveticaNeueLight.ttf", 40)
    name_font = ImageFont.truetype("fonts/HelveticaNeueBold.ttf", 40)
    username_font = ImageFont.truetype("fonts/HelveticaNeueLight.ttf", 35)
    date_font = ImageFont.truetype("fonts/HelveticaNeueLight.ttf", 30)

    words = tweet.split(" ")
    to_remove = []
    tweet_lines = []
    rectangle_w = 0
    for word in words:
        if word.startswith("https://t.co"):
            response = requests.get(word)
            if "photo" not in response.url and "video" not in response.url:
                to_remove.append(word)
                continue
            to_remove.append(word)
    for tr in to_remove:
        words.remove(tr)
    tweet = " ".join(words)
    media_url = media_url.replace("[", "").replace("]",
                                                   "").replace("'",
                                                               "").split(",")
    medias = len(media_url)
    if medias == 1 and media_url[0] == "":
        medias = 0
    media_sizes = []
    media_no = 1
    for url in media_url:
        if url != "":
            medianame = 'cache/' + str(media_no) + ".png"
            urllib.request.urlretrieve(url, medianame)
            im = cv2.imread(medianame).shape
            media_sizes.append([im[0], im[1]])
        media_no += 1
    tweet2 = tweet[:]
    tweet_lines2 = tweet_lines[:]
    amo_lines = tweet_in_lines(tweet2, tweet_lines2, tw_font)
    for media_size in media_sizes:
        w_factor = 1
        h_factor = 1
        if medias == 2 or medias == 4 or medias == 3:
            w_factor = 2
        if medias == 4 or medias == 3:
            h_factor = 2
        if media_size[1] > int(700 / w_factor):
            how_smaller = int(700 / w_factor) / media_size[1]
            media_size[1] = int(700 / w_factor)
            media_size[0] = int(how_smaller * media_size[0])
        if media_size[0] > int((500 - amo_lines * 70) / h_factor):
            amo_lines2 = amo_lines
            if amo_lines2 > 6:
                amo_lines2 = 6
            how_smaller = int(
                (500 - amo_lines2 * 70) / h_factor) / media_size[0]
            media_size[0] = int((500 - amo_lines2 * 70) / h_factor)
            media_size[1] = int(how_smaller * media_size[1])
    width = 1080
    height = 1080
    urllib.request.urlretrieve(profile_image, "cache/p_img.png")
    profile_image = Image.open("cache/p_img.png", 'r')
    profile_image = circle_image(profile_image)
    profile_image = profile_image.resize((180, 180))
    img = Image.new(mode="RGB", size=(width, height), color=(r, g, b))
    img_w, img_h = profile_image.size
    bg_w, bg_h = img.size
    # offset = ((bg_w - img_w) // 6, (bg_h - img_h) // 6)
    draw = ImageDraw.Draw(img)
    tweet_size = get_text_dimensions(tweet, tw_font)
    tweet_w = (width - 900) // 2
    tweet_h = (height - tweet_size[1]) // 2 + 50
    if medias == 1:
        media_offset_h = media_sizes[0][0]
    elif medias == 2:
        if media_sizes[0][0] > media_sizes[1][0]:
            media_offset_h = media_sizes[0][0]
        else:
            media_offset_h = media_sizes[1][0]
    elif medias == 4:
        if media_sizes[0][0] > media_sizes[1][0]:
            media_offset_h = media_sizes[0][0]
        else:
            media_offset_h = media_sizes[1][0]
        if media_sizes[2][0] > media_sizes[3][0]:
            media_offset_h += media_sizes[2][0]
        else:
            media_offset_h += media_sizes[3][0]
        media_offset_h += 20
    elif medias == 3:
        if media_sizes[0][0] > media_sizes[1][0]:
            media_offset_h = media_sizes[0][0]
        else:
            media_offset_h = media_sizes[1][0]
        media_offset_h += media_sizes[2][0]
        media_offset_h += 20
    else:
        media_offset_h = 0
    if tweet_size[0] <= 900 and "\n" not in tweet:
        tweet_w = (width - tweet_size[0]) // 2
        tweet_h = (height - tweet_size[1] - media_offset_h) // 2 + 50
        if tweet_size[0] <= 700:
            tweet_w = (width - 700) // 2
            tweet_h = (height - tweet_size[1] - media_offset_h) // 2 + 50
            draw.rectangle(((tweet_w - 60, tweet_h - 300),
                            (tweet_w + 700 + 60,
                             tweet_h + tweet_size[1] + media_offset_h + 200)),
                           fill="white")
            rectangle_w = tweet_w + 700 + 60
        else:
            draw.rectangle(((tweet_w - 60, tweet_h - 300),
                            (tweet_w + tweet_size[0] + 60,
                             tweet_h + tweet_size[1] + media_offset_h + 200)),
                           fill="white")
            rectangle_w = tweet_w + tweet_size[0] + 60
        with Pilmoji(img) as pilmoji:
            pilmoji.text((tweet_w, tweet_h), tweet, (0, 0, 0), font=tw_font)
    else:
        tweet_in_lines(tweet, tweet_lines, tw_font)
        tweet_w = (width - 900) // 2
        tweet_h = (height - (tweet_size[1] + 15) * len(tweet_lines) -
                   media_offset_h) // 2 + 50
        draw.rectangle(((tweet_w - 60, tweet_h - 300),
                        (tweet_w + 900 + 60, tweet_h + media_offset_h +
                         (tweet_size[1] + 15) * len(tweet_lines) + 200)),
                       fill="white")
        rectangle_w = tweet_w + 900 + 60
        line_no = 0
        for tweet_line in tweet_lines:
            with Pilmoji(img) as pilmoji:
                pilmoji.text(
                    (tweet_w, tweet_h + (tweet_size[1] + 15) * line_no),
                    tweet_line, (0, 0, 0),
                    font=tw_font)

            line_no += 1
    img.paste(profile_image, (tweet_w, tweet_h - 250), profile_image)
    Pilmoji(img).text((tweet_w + 200, tweet_h - 200),
                      name, (0, 0, 0),
                      font=name_font)
    Pilmoji(img).text((tweet_w + 200, tweet_h - 140),
                      "@" + username, (83, 100, 113),
                      font=username_font)
    if len(tweet_lines) == 0:
        len_tweet_lines = 1
    else:
        len_tweet_lines = len(tweet_lines)
    fr_offset = tweet_h + (tweet_size[1] + 15) * (1 + len_tweet_lines)
    if medias == 1:
        media = Image.open("cache/1.png", 'r')
        media = media.resize((media_sizes[0][1], media_sizes[0][0]))
        img.paste(media, ((width - media_sizes[0][1]) // 2, tweet_h +
                          (tweet_size[1] + 15) * len_tweet_lines))
        fr_offset = tweet_h + (tweet_size[1] +
                               15) * len_tweet_lines + media_offset_h + 50
    if medias == 2:
        media_1 = Image.open("cache/1.png", 'r')
        media_2 = Image.open("cache/2.png", 'r')
        media_1 = media_1.resize((media_sizes[0][1], media_sizes[0][0]))
        media_2 = media_2.resize((media_sizes[1][1], media_sizes[1][0]))
        img.paste(media_1,
                  ((width - media_sizes[0][1] - media_sizes[1][1] - 20) // 2,
                   tweet_h + (tweet_size[1] + 15) * (len_tweet_lines)))
        img.paste(media_2,
                  ((width - media_sizes[0][1] - media_sizes[1][1]) // 2 +
                   media_sizes[0][1] + 20, tweet_h + (tweet_size[1] + 15) *
                   (len_tweet_lines)))
        fr_offset = tweet_h + (tweet_size[1] +
                               15) * (len_tweet_lines) + media_offset_h + 50
    if medias == 4 or medias == 3:
        media_1 = Image.open("cache/1.png", 'r')
        media_2 = Image.open("cache/2.png", 'r')
        media_3 = Image.open("cache/3.png", 'r')
        media_1 = media_1.resize((media_sizes[0][1], media_sizes[0][0]))
        media_2 = media_2.resize((media_sizes[1][1], media_sizes[1][0]))
        media_3 = media_3.resize((media_sizes[2][1], media_sizes[1][0]))
        if medias == 4:
            media_4 = Image.open("cache/4.png", 'r')
            media_4 = media_4.resize((media_sizes[3][1], media_sizes[1][0]))
            img.paste(
                media_4,
                ((width - media_sizes[2][1] - media_sizes[3][1]) // 2 +
                 media_sizes[2][1] + 20, 20 + media_sizes[1][0] + tweet_h +
                 (tweet_size[1] + 15) * (len_tweet_lines)))
            img.paste(media_3,
                      ((width - media_sizes[2][1] - media_sizes[3][1] - 20) //
                       2, 20 + media_sizes[0][0] + tweet_h +
                       (tweet_size[1] + 15) * (len_tweet_lines)))
        else:
            img.paste(media_3, ((width - media_sizes[2][1]) // 2,
                                20 + media_sizes[0][0] + tweet_h +
                                (tweet_size[1] + 15) * (len_tweet_lines)))
        img.paste(media_1,
                  ((width - media_sizes[0][1] - media_sizes[1][1] - 20) // 2,
                   tweet_h + (tweet_size[1] + 15) * (len_tweet_lines)))
        img.paste(media_2,
                  ((width - media_sizes[0][1] - media_sizes[1][1]) // 2 +
                   media_sizes[0][1] + 20, tweet_h + (tweet_size[1] + 15) *
                   (len_tweet_lines)))
        fr_offset = tweet_h + (tweet_size[1] +
                               15) * (len_tweet_lines) + media_offset_h + 50

    if showFavsRt:
        rectangle_w = rectangle_w - (tweet_w - 60)
        fav_img = Image.open("resources/fav.png", 'r')
        rt_img = Image.open("resources/rt.png", 'r')
        fav_img = fav_img.resize((50, 50))
        rt_img = rt_img.resize((66, 40))
        img.paste(fav_img,
                  ((tweet_w - 60) + int(rectangle_w * 0.3), fr_offset + 50),
                  fav_img)
        img.paste(rt_img,
                  ((tweet_w - 60) + int(rectangle_w * 0.6), fr_offset + 50),
                  rt_img)
        draw.text(
            ((tweet_w - 60) + int(rectangle_w * 0.3) + 70, fr_offset + 50),
            str(favs), (0, 0, 0),
            font=username_font)
        draw.text(
            ((tweet_w - 60) + int(rectangle_w * 0.6) + 80, fr_offset + 50),
            str(retweets), (0, 0, 0),
            font=username_font)
    if show_date:
        tweet_timestamp2 = tweet_timestamp.split("-")
        tweet_timestamp3 = tweet_timestamp2[2].split(" ")
        tweet_timestamp4 = tweet_timestamp3[1].split(":")
        months = [
            "Jan.", "Feb.", "März", "Apr.", "Mai", "Juni", "Juli", "Aug.",
            "Sep.", "Okt.", "Nov.", "Dez."
        ]
        if int(tweet_timestamp4[0]) < 12:
            tweet_timestamp4[1] += " vorm."
        else:
            tweet_timestamp4[1] += " nachm."
            if int(tweet_timestamp4[0]) != 12:
                tweet_timestamp4[0] = str(int(tweet_timestamp4[0]) - 12)
        if int(tweet_timestamp4[0]) == 0:
            tweet_timestamp4[0] = "12"

        tweet_timestamp = tweet_timestamp4[0] + ":" + tweet_timestamp4[
            1] + " · " + tweet_timestamp3[0] + ". " + months[
                              int(tweet_timestamp2[1]) - 1] + " " + tweet_timestamp2[0]
        draw.text((tweet_w, fr_offset - 40),
                  tweet_timestamp, (83, 100, 113),
                  font=date_font)
    if not os.path.exists('tweet_images/' + username):
        os.makedirs('tweet_images/' + username)
    img.save("tweet_images/" + username + "/" + str(tweet_id) + ".jpg")
    print("tweet_images/" + username + "/" + str(tweet_id) + ".jpg saved.")
