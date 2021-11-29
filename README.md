# Tweet2Image
Convert tweets to Instagram-friendly images.

## How to use
If you want to use this repository as a submodule, don't forget to put the **fonts** directory, the **resources** directory and **credentials.py** in your working directory.  

There are two main functions in tweet_image.py: 
* def tweets_to_images(file, handle, name, showFavsRt, show_date)
* def tweet_to_image(name, username, showFavsRt, show_date, tweet, tweet_timestamp, favs, retweets, profile_image, tweet_id, media_url, r, g, b)

### tweets_to_images
* *file*: File with the tweets. You can generate such a file with this module which I have developed: https://github.com/EinGuterWaran/FetchTweets
* *handle*: The Twitter handle/username of the user
* *name*: The name of the user (not the Twitter handle) which will be on the image. You can let this empty to retrieve the original name via the Twitter API
* *showFavsRt*: **True** if you want to show the likes and retweets on the image, **False** if not
* *show_date*: **True** if you want to show the date of the tweet on the image, **False** if not  

tweets_to_images uses tweet_to_image.

### tweet_to_image
* *name*: The name of the user (not the Twitter handle) which will be on the image. You can let this empty to retrieve the original name via the Twitter API
* *username*: The Twitter handle/username of the user
* *showFavsRt*: **True** if you want to show the likes and retweets on the image, **False** if not
* *showDate*: **True** if you want to show the date of the tweet on the image, **False** if not
* *tweet*: The tweet itself
* *tweet_timestamp*: This format -> 2021-08-08 16:08:24+00:00
* *favs*: How many likes
* *retweets*: How many retweets
* *profile_image*: Path to profile image
* *tweet_id*: Id of the tweet (it's in the url of the tweet)
* *media_url*: Array with the urls of the images in the tweet
* *r, g, b*: Color of the background behind the tweet
