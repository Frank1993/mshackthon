# -*- coding: utf-8 -*-
#
import os, os.path
import uuid
import hashlib
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import urllib
from tornado.options import define, options

from collections import defaultdict

from face_profile import get_profile

from sim_image import find_similar_image

from weixin_sdk.public import WxBasic

define("port", default=443, help="run on the given port", type=int)

image_dir = os.path.abspath('../data/receive_image')
users =defaultdict(dict)
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/image_similar/(.*)", tornado.web.StaticFileHandler, {'path':r"../data/receive_image/"}),
            (r"/", MainHandler),
        ]
        settings = dict(
            debug=True,
            img_dir=image_dir    #这儿改成想要存图片的地址
        )
        super(Application, self).__init__(handlers, **settings)
        self.maybe_create_dir()

    def maybe_create_dir(self):
        img_dir = self.settings['img_dir']
        if not os.path.exists(img_dir):
            os.mkdir(img_dir)


class BaseHandler(tornado.web.RequestHandler):

    def get_img_path(self, filename):
        return os.path.join(self.settings["img_dir"], filename)

    def gen_unique_name(self):
        return hashlib.md5(str(uuid.uuid4())).hexdigest()

    def image_profile(self, image_path):

        return get_profile(image_path)

    def find_simlilar_image(self, file_path):
        #实现函数find_simlilar_image
        return find_similar_image(file_path)


class MainHandler(BaseHandler):

    #curl -F img=@ThisImgName.jpg http://localhost:8888/?action=uploadImg
    #curl -d '{"samegender":"0","imgpath":"fdsfasfsd"}' http://localhost:8888/?action=getSimilar
    def prepare(self):
        self.wechat = WxBasic(appid='wxc6bda0648ddce174',
                              appsecret='2817bd8733126ad630f9d23b149dc3d1',
                              token='hack')
        
    def get(self):
        #首次接入验证,传入url上的query字符串键值对
        if self.wechat.check_signature(self.query_arguments):
            echo_str = self.get_query_argument('echostr', '')
            self.write(echo_str)
        else:
            self.write('wrong, request not from wechat!')

    def post(self):
        """
        action = self.get_query_argument('action')
        if action == 'uploadImg':
            self.receive_img()
        elif action == 'getSimilar':
            self.get_similar_img()
        #elif action.endwith(".jpg"):
            #self.send_image(action)
        else:
            self.set_status(404)
        """

        self.wechat.parse_data(self.request.body)
        message = self.wechat.message
        #收到消息后针对不同消息类型进行处理
        if message.msgType == 'text':
            content = message.content
            if content == "1":
                users[message.fromUserName]["func"]="1"
                self.write(self.wechat.pack_text("请输入一张图片："))
            elif content == "2":
                users[message.fromUserName]["func"] = "2"
                self.write(self.wechat.pack_text("请输入一张图片："))
            elif content == "3":
                users[message.fromUserName]["func"] = "3"
                self.write(self.wechat.pack_text("3.1:\"宝贝回家公益活动\"\n3.2:\"对于雾霾我有话说\""))
            else:
                self.write(self.wechat.pack_text("1.最美的容颜\n2.相似的人\n3.找找感兴趣的话题"))

            #print u'收到文本消息:%s' % content
            #self.write(self.wechat.pack_text(content))
            return
        elif message.msgType == 'image':
            imageUrl = message.picUrl

            if imageUrl in users[message.fromUserName]:
                if users[message.fromUserName]["func"] == "1":
                    profile_message = users[message.fromUserName][imageUrl]["profile_message"]
                    self.write(self.wechat.pack_text(profile_messages))

                elif users[message.fromUserName]["func"] == "2":
                    sim_message = users[message.fromUserName][imageUrl]["sim_message"]
                    self.write(self.wechat.pack_text(sim_message))
            else:
                imagePath = self.receive_img(imageUrl)

                users[message.fromUserName][imageUrl] = {}
                users[message.fromUserName][imageUrl]["imagePath"] = imagePath

                if users[message.fromUserName]["func"]  == "1":
                    profile = self.image_profile(imagePath)

                    profile_messages = self.profileParse(profile)

                    users[message.fromUserName][imageUrl]["profile_message"] = profile_messages
                    self.write(self.wechat.pack_text(profile_messages))

                elif users[message.fromUserName]["func"]  == "2":
                    similarImage = self.get_similar_img(imagePath)
                    sim_message = "我们找到了如下这些相似图片：\n"

                    for image in similarImage:
                        image = "http://115.28.212.24/image_similar/" + image.split('/')[-1]
                        sim_message += image 
                        sim_message + "\n"

                    users[message.fromUserName][imageUrl]["sim_message"] = sim_message

                    self.write(self.wechat.pack_text(sim_message))

        elif message.msgType == 'event':
            pass

    def profileParse(self,profile):
        message = ""
        if profile["glasses"]== "0":
            message += "不带眼镜，"
        else:
            message += "带眼镜，"

        if profile["skin"] == "0":
            message += "肤色正常,"
        elif profile["skin"] == "1":
            message += "肌肤亮白,"
        else:
            message += "肤色健康,"

        message += "给您的颜值评分 %s分"%profile['face_score']

        return message


    def send_image(self,imageName):
        imagePath = self.get_img_path(imageName)
        self.write({"imageName":imagePath})
    def receive_img(self,imageUrl):
        

        filename = self.gen_unique_name()
        filepath = self.get_img_path(filename)+".jpg"
        try:
            urllib.urlretrieve(imageUrl,filepath)
            return filepath
        except Exception, e:
            self.set_status(500)
            return self.write('save img error')

        



    def get_similar_img(self,imagePath):
        newpath = self.find_simlilar_image(imagePath)
        print "similar image:",newpath
        return newpath


def main():
    tornado.options.parse_command_line()
    print 'will listening on port %s...' % options.port
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
