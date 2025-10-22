# coding:utf-8
import os
import math
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.properties import NumericProperty, ListProperty, ObjectProperty

# -------------------- 配置 --------------------
ORIGINAL_WIDTH = 1400
ORIGINAL_HEIGHT = 700
Window.size = (ORIGINAL_WIDTH, ORIGINAL_HEIGHT)

# 颜色
DARK_WOOD = (50/255, 35/255, 25/255)
LIGHT_WOOD = (120/255, 90/255, 60/255)
GOLD = (200/255, 170/255, 80/255)
BRASS = (180/255, 150/255, 60/255)
DARK_LEATHER = (50/255, 40/255, 30/255)
BUTTON_COLOR = (100/255, 80/255, 60/255)
BUTTON_HOVER = (150/255, 120/255, 90/255)
TEXT_COLOR = (220/255, 220/255, 210/255)

# -------------------- 工具函数 --------------------
def resource_path(filename):
    return os.path.join(os.getcwd(), filename)

# -------------------- 物品类 --------------------
class Item:
    def __init__(self, name, description, position, hotspot_shape="circle", hotspot_size=50, polygon_points=None, image_paths=None):
        self.name = name
        self.description = description
        self.position = position
        self.hotspot_shape = hotspot_shape
        self.hotspot_size = hotspot_size
        self.polygon_points = polygon_points or []
        self.image_paths = image_paths or []
        self.inventory_image = None
        self.images = []
        if self.image_paths:
            for path in self.image_paths:
                try:
                    tex = CoreImage(path).texture
                    self.images.append(tex)
                except:
                    pass
            if self.images:
                self.inventory_image = self.images[0]

    def check_collision(self, touch_pos):
        x, y = touch_pos
        px, py = self.position
        if self.hotspot_shape == "circle":
            dx = x - px
            dy = y - py
            return math.sqrt(dx*dx + dy*dy) <= self.hotspot_size/2
        elif self.hotspot_shape == "polygon":
            return self.point_in_polygon(touch_pos)
        return False

    def point_in_polygon(self, point):
        x, y = point
        n = len(self.polygon_points)
        inside = False
        if n < 3:
            return False
        p1x, p1y = self.polygon_points[0]
        for i in range(n+1):
            p2x, p2y = self.polygon_points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x==p2x or x<=xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

# -------------------- 场景类 --------------------
class Scene:
    def __init__(self, name, background_image=None):
        self.name = name
        self.background_image_path = background_image
        self.items = []
        self.bg_texture = None
        if self.background_image_path:
            try:
                self.bg_texture = CoreImage(self.background_image_path).texture
            except:
                self.bg_texture = None

    def add_item(self, item):
        self.items.append(item)

# -------------------- 物品栏 --------------------
class Inventory:
    def __init__(self):
        self.items = []
        self.item_size = 60
        self.spacing = 5
        self.position = (20, 40)
        self.max_items = 9

    def add_item(self, item):
        if len(self.items) < self.max_items and not any(i.name == item.name for i in self.items):
            self.items.append(item)

# -------------------- 消息框 --------------------
class MessageBox:
    def __init__(self):
        self.visible = False
        self.item = None
        self.rect = [ORIGINAL_WIDTH//2 - 400, ORIGINAL_HEIGHT//2 - 300, 800, 600]
        self.scale = 0.0
        self.state = "closed"  # closed, opening, open, closing
        self.speed = 0.15

    def show(self, item):
        self.item = item
        self.visible = True
        self.state = "opening"
        self.scale = 0.0

    def close(self):
        self.state = "closing"

    def update(self):
        if self.state == "opening":
            self.scale += self.speed
            if self.scale >= 1.0:
                self.scale = 1.0
                self.state = "open"
        elif self.state == "closing":
            self.scale -= self.speed
            if self.scale <= 0.0:
                self.scale = 0.0
                self.state = "closed"
                self.visible = False
                self.item = None

# -------------------- 游戏主 Widget --------------------
class GameWidget(Widget):
    scenes = ListProperty([])
    current_scene_index = NumericProperty(0)
    inventory = ObjectProperty(None)
    message_box = ObjectProperty(None)
    correct_sound = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # 加载音效
        try:
            self.correct_sound = SoundLoader.load(resource_path("correct.mp3"))
        except:
            self.correct_sound = None

        # 初始化场景
        self.scenes = [
            Scene("指挥室", resource_path("cabin.png")),
            Scene("船舱", resource_path("bridge.png"))
        ]

        # 示例物品
        self.scenes[0].add_item(Item("协议", "", (400,420), "polygon", polygon_points=[(370,400),(570,400),(570,440),(370,440)], image_paths=[resource_path("protocol.png")]))
        self.scenes[0].add_item(Item("指南针", "", (760,520), "circle", hotspot_size=70, image_paths=[resource_path("zhinanzhen1.png"), resource_path("zhinanzhen2.png")]))
        self.scenes[1].add_item(Item("黄金", "", (200,200), "polygon", polygon_points=[(600,330),(850,330),(850,390),(600,390)], image_paths=[resource_path("huangjin1.png"), resource_path("huangjin2.png")]))

        # 物品栏
        self.inventory = Inventory()

        # 消息框
        self.message_box = MessageBox()

        # 场景切换按钮
        self.next_button = Item("下一场景", "", (ORIGINAL_WIDTH-60, ORIGINAL_HEIGHT//2), "circle", hotspot_size=50)
        self.prev_button = Item("上一场景", "", (ORIGINAL_WIDTH-60, ORIGINAL_HEIGHT//2+80), "circle", hotspot_size=50)

        # 更新帧
        Clock.schedule_interval(self.update, 1/60)

    def next_scene(self):
        self.current_scene_index = (self.current_scene_index + 1) % len(self.scenes)

    def prev_scene(self):
        self.current_scene_index = (self.current_scene_index - 1) % len(self.scenes)

    def update(self, dt):
        self.canvas.clear()
        self.message_box.update()
        with self.canvas:
            # 背景
            scene = self.scenes[self.current_scene_index]
            if scene.bg_texture:
                Rectangle(texture=scene.bg_texture, pos=(0,0), size=Window.size)
            else:
                Color(*DARK_WOOD)
                Rectangle(pos=(0,0), size=Window.size)

            # 绘制场景物品热点（调试可用）
            # for item in scene.items:
            #     Color(1,0,0,0.3)
            #     Ellipse(pos=(item.position[0]-item.hotspot_size/2, item.position[1]-item.hotspot_size/2),
            #             size=(item.hotspot_size,item.hotspot_size))

            # 绘制物品栏
            for idx, item in enumerate(self.inventory.items):
                if item.inventory_image:
                    x = self.inventory.position[0]
                    y = self.inventory.position[1] + idx*(self.inventory.item_size+self.inventory.spacing)
                    Rectangle(texture=item.inventory_image, pos=(x,y), size=(self.inventory.item_size,self.inventory.item_size))

            # 消息框
            if self.message_box.visible and self.message_box.item and self.message_box.scale > 0.0:
                x, y, w, h = self.message_box.rect
                sw = w * self.message_box.scale
                sh = h * self.message_box.scale
                sx = x + (w - sw)/2
                sy = y + (h - sh)/2
                Color(0.1,0.1,0.1,0.8)
                Rectangle(pos=(sx,sy), size=(sw,sh))
                # 显示图片
                if self.message_box.item.images:
                    img = self.message_box.item.images[0]
                    iw = sw*0.8
                    ih = sh*0.8
                    ix = sx + (sw - iw)/2
                    iy = sy + (sh - ih)/2
                    Rectangle(texture=img, pos=(ix,iy), size=(iw,ih))

    def on_touch_down(self, touch):
        scene = self.scenes[self.current_scene_index]

        # 消息框关闭
        if self.message_box.visible:
            self.message_box.close()
            return True

        # 场景切换按钮
        if self.next_button.check_collision(touch.pos):
            self.next_scene()
            return True
        if self.prev_button.check_collision(touch.pos):
            self.prev_scene()
            return True

        # 检查物品拾取
        for item in scene.items:
            if item.check_collision(touch.pos):
                self.inventory.add_item(item)
                if self.correct_sound:
                    self.correct_sound.play()
                self.message_box.show(item)
                return True

# -------------------- Kivy App --------------------
class MyGameApp(App):
    def build(self):
        return GameWidget()

# -------------------- 启动 --------------------
if __name__ == "__main__":
    MyGameApp().run()
