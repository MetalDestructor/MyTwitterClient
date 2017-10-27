import wx
import tweepy
import twitterSide
import wx.lib.scrolledpanel
import urllib2
import StringIO
import functools

images = ["icons/home.png", "icons/mention.png", "icons/messages.png", "icons/fav.png"]
             
api = twitterSide.api
me = api.me()

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Twitter Client", size=(1150, 750), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.SetBackgroundColour('#33ccff')

        self.navPanel = wx.Panel(self, -1, pos=(0,0), size=(63, 280), style=wx.BORDER_DOUBLE)
        self.navPanel.SetBackgroundColour('#33ccff')

        self.BindingNav(self.navPanel, images[0], (0,0), self.Home)
        self.BindingNav(self.navPanel, images[1], (0,70), self.Mentions)
        self.BindingNav(self.navPanel, images[2], (0,140), self.Messages)
        self.imgProfile = self.LoadImageFromURL(api.me().profile_image_url)
        self.buttonProfile = wx.BitmapButton(self.navPanel, -1, self.imgProfile, pos=(0, 210), size=(55,55), style=wx.NO_BORDER)
        self.buttonProfile.Bind(wx.EVT_BUTTON, self.Profile)

        self.homePanel = self.createNewPanel(self, pos=(67,0), size=(650,710), color='#33ccff')
        self.mentionsPanel = self.createNewPanel(self, pos=(67,0), size=(650,710), color='#33ccff')
        self.messagesPanel = self.createNewPanel(self, pos=(67,0), size=(650,710), color='#33ccff')
        self.profilePanel = self.createNewPanel(self, pos=(67,0), size=(650,710), color='#33ccff')
        self.peekProfiles = self.createNewPanel(self, pos=(720,0), size=(400, 500), color='#33ccff')
        self.peekProfiles.Show(True)
        self.Home(wx.EVT_ACTIVATE_APP)

    def Home(self, e):
        self.closeAll(self.mentionsPanel, self.messagesPanel, self.profilePanel)
        self.homePanel.Show(True)
        self.tweets = api.home_timeline(include_entities=True)
        self.createTweetsPanel(self.tweets, 5, 40, 633, 100, self.homePanel, self.ViewProfile, self.OnFavorite)
        

    def Mentions(self, e):
        self.closeAll(self.homePanel, self.messagesPanel, self.profilePanel)
        self.mentionsPanel.Show(True)
        self.mentions = tweepy.Cursor(api.search, q="@JustMetall").items()
        self.createTweetsPanel(self.mentions, 5, 40, 633, 100, self.mentionsPanel, self.ViewProfile, self.OnFavorite)
        
    def Messages(self, e):
        self.closeAll(self.homePanel, self.mentionsPanel, self.profilePanel)
        self.messagesPanel.Show(True)
        self.myMessages = api.direct_messages()
        self.createMessagesPanel(self.myMessages, 5, 40, 633, 100, self.messagesPanel, self.ViewProfile)

    def Profile(self, e):
        self.closeAll(self.homePanel, self.messagesPanel, self.mentionsPanel)
        self.profilePanel.Show(True)
        self.profilePanel.SetBackgroundColour('#' + me.profile_link_color)
        #My Profile Picture
        self.profilePic = self.LoadImageFromURL(me.profile_image_url)
        self.profilePic = self.scaleBitmap(self.profilePic, 100, 100)
        self.avatar = wx.StaticBitmap(self.profilePanel, -1, self.profilePic, pos=(4, 4))
        #My Name
        self.name = wx.StaticText(self.profilePanel, -1, label=me.name, pos=(110, 4))
        self.name.SetForegroundColour('#' + me.profile_text_color)
        self.font = wx.Font(25, family=wx.DECORATIVE, style=wx.NORMAL, weight=wx.BOLD)
        self.name.SetFont(self.font)
        #My Tag
        self.nickname = wx.StaticText(self.profilePanel, -1, label='@' + me.screen_name, pos=(110, 45))
        self.nickname.SetForegroundColour('#' + me.profile_text_color)
        #My Follower count
        self.fLabel = wx.StaticText(self.profilePanel, -1, pos=(555, 42))
        self.followers = "Followers: " + str(me.followers_count)
        self.fLabel.SetLabel(self.followers)
        self.fLabel.SetForegroundColour('#' + me.profile_text_color)
        #Tweet
        self.tweetText = wx.TextCtrl(self.profilePanel, pos=(4, 110), size=(637, 95), style=wx.TE_MULTILINE)
        self.tweetButton = wx.Button(self.profilePanel, pos=(535, 208), label="Tweet")
        self.tweetButton.Bind(wx.EVT_BUTTON, functools.partial(self.OnTweet, tweetText=self.tweetText))
        #My Timeline
        self.profileTimeline = api.user_timeline(me.id)
        self.peekedProfileTweets = self.createNewPanel(self.profilePanel, pos=(5, 240), size=(630, 550), color='#' + me.profile_link_color)
        self.peekedProfileTweets.Show(True)
        self.createTweetsPanel(self.profileTimeline, 5, 40, 620, 100, self.peekedProfileTweets, self.ViewProfile, self.OnFavorite)

    def OnTweet(self, e, tweetText):
        api.update_status(tweetText.GetValue())
        tweetText.Clear()
        print "Status updates successfully"

    def ViewProfile(self, e, tweet):
        self.peekProfiles.Show(True)
        #Working of data
        self.human = ""
        if isinstance(tweet, tweepy.models.DirectMessage):
            self.human = tweet.sender
        else:
            self.human = tweet.author
        #Panel whick will change on different profile
        self.temp = wx.Panel(self.peekProfiles, -1, pos=(0,0), size=(400, 500))
        self.temp.Show(True)
        self.temp.SetBackgroundColour('#' + self.human.profile_link_color)
        #Profile's profile picture
        self.profilePic = self.LoadImageFromURL(self.human.profile_image_url)
        self.profilePic = self.scaleBitmap(self.profilePic, 60, 60)
        self.avatar = wx.StaticBitmap(self.temp, -1, self.profilePic, pos=(0, 0))
        #Profile's name
        self.name = wx.StaticText(self.temp, -1, label=self.human.name, pos=(65, 0))
        self.name.SetForegroundColour('#' + self.human.profile_text_color)
        self.font = wx.Font(15, family=wx.DECORATIVE, style=wx.NORMAL, weight=wx.BOLD)
        self.name.SetFont(self.font)
        #Profile's tag
        self.nickname = wx.StaticText(self.temp, -1, label='@' + self.human.screen_name, pos=(65, 25))
        self.nickname.SetForegroundColour('#' + self.human.profile_text_color)
        #Profile's followers
        self.fLabel = wx.StaticText(self.temp, -1, pos=(255, 25), style=wx.ALIGN_LEFT)
        self.followers = "Followers: " + str(self.human.followers_count)
        self.fLabel.SetLabel(self.followers)
        self.fLabel.SetForegroundColour('#' + self.human.profile_text_color)
        #Profile's Follow Button
        self.follow = wx.Button(self.temp, -1, "Follow/Unfollow", pos=(0, 70))
        self.follow.Bind(wx.EVT_BUTTON, functools.partial(self.Follow, tweet=tweet))
        #Profile's Timeline
        self.profileTimeline = api.user_timeline(self.human.id)
        self.peekedProfileTweets = self.createNewPanel(self.temp, pos=(5, 100), size=(390, 390), color='#' + self.human.profile_link_color)
        self.peekedProfileTweets.Show(True)
        self.createTweetsPanel(self.profileTimeline, 5, 40, 375, 80, self.peekedProfileTweets, self.ViewProfile, self.OnFavorite)

    def scaleBitmap(self, bitmap, width, height):
        self.image = wx.ImageFromBitmap(bitmap)
        self.image = self.image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        self.result = wx.BitmapFromImage(self.image)
        return self.result

    def OnFavorite(self, e, tweet):
        if tweet.favorited is False:
            api.create_favorite(tweet.id)
            tweet.favorited = True
            print "You liked tweet of " + tweet.author.name
        else:
            api.destroy_favorite(tweet.id)
            tweet.favorited = False
            print "You unliked tweet of " + tweet.author.name

    def Follow(self, e, tweet):
        if tweet.author.following is False:
            api.create_friendship(tweet.author.id)
            tweet.author.following = True
            print "Now you follow " + tweet.author.name
        else:
            api.destroy_friendship(tweet.author.id)
            tweet.author.following = False
            print "You just unfollowed " + tweet.author.name

    def BindingNav(self, panel, img, pos, func):
        image = wx.Image(img, wx.BITMAP_TYPE_ANY).Scale(45, 45)
        button = wx.BitmapButton(panel, -1, wx.BitmapFromImage(image), pos=pos, style=wx.NO_BORDER)
        button.Bind(wx.EVT_BUTTON, func)

    def LoadImageFromURL(self, url):
        buf = urllib2.urlopen(url).read()
        sbuf = StringIO.StringIO(buf)
        img = wx.ImageFromStream(sbuf).ConvertToBitmap()
        return img

    def createNewPanel(self, parent, pos, size, color):
        panel = wx.lib.scrolledpanel.ScrolledPanel(parent, -1, pos=pos, size=size, style=wx.BORDER_DOUBLE)
        panel.Show(False)
        panel.SetBackgroundColour(color)
        return panel

    def createTweetsPanel(self, tweets, x, posx, width, height, panel, avatarFunc, favFunc):
        self.bSizer = wx.BoxSizer(wx.VERTICAL)

        for tweet in tweets:
            self.tweetPanel = wx.Panel(panel, -1, pos=(2,x), size=(width, height), style=wx.BORDER_DOUBLE)
            self.tweetPanel.SetBackgroundColour('White')
            self.tweetA = self.LoadImageFromURL(tweet.user.profile_image_url)
            self.avatar = wx.StaticBitmap(self.tweetPanel, -1, self.tweetA, pos=(0, height/5), size=(height/2, height/2)) 
            self.avatar.Bind(wx.EVT_LEFT_UP, functools.partial(avatarFunc, tweet=tweet))
            self.text = wx.StaticText(self.tweetPanel, label=tweet.text, pos=(height/2 + 10,0))
            ###For showing url to the article
            # for t in tweet.entities['urls']:
            #     self.url = wx.HyperlinkCtrl(self.tweetPanel, -1, t['url'], pos=(height/2 + 10, height/2))
            self.imgFav = wx.Image(images[3], wx.BITMAP_TYPE_ANY).Scale(20, 20)
            self.fav = wx.StaticBitmap(self.tweetPanel, -1, wx.BitmapFromImage(self.imgFav), pos=(width-30, height-30))
            self.fav.Bind(wx.EVT_LEFT_UP, functools.partial(favFunc, tweet=tweet))
            self.text.Wrap(width - 50)
            self.bSizer.Add(self.tweetPanel, 0 , wx.ALL, 5)
            x = x+posx

        panel.SetSizer(self.bSizer)
        panel.SetupScrolling()
    
    def createMessagesPanel(self, messages, x, posx, width, height, panel, avatarFunc):
        self.bSizer = wx.BoxSizer(wx.VERTICAL)

        for message in messages:
            self.tweetPanel = wx.Panel(panel, -1, pos=(2,x), size=(width, height), style=wx.BORDER_DOUBLE)
            self.tweetPanel.SetBackgroundColour('White')
            self.tweetA = self.LoadImageFromURL(message.sender.profile_image_url)
            self.avatar = wx.StaticBitmap(self.tweetPanel, -1, self.tweetA, pos=(0, height/5), size=(height/2, height/2)) 
            self.avatar.Bind(wx.EVT_LEFT_UP, functools.partial(avatarFunc, tweet=message))
            self.text = wx.StaticText(self.tweetPanel, label=message.text, pos=(height/2 + 10,0))
            self.text.Wrap(width - 50)
            self.bSizer.Add(self.tweetPanel, 0 , wx.ALL, 5)
            x = x + posx;

        panel.SetSizer(self.bSizer)
        panel.SetupScrolling()

    def closeAll(self, panel1, panel2, panel3):
        panel1.Show(False)
        panel2.Show(False)
        panel3.Show(False)

class MyApp(wx.App):
    def OnInit(self):
        frame = MainFrame()
        frame.SetIcon(wx.Icon('icons/twitter.ico', wx.BITMAP_TYPE_ICO))
        frame.Show(True)
        frame.Center()
        return True