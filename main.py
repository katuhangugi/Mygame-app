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
from kivy.config import Config

# -------------------- 移动设备配置 --------------------
# 设置适合移动设备的配置
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')

# 检测平台并设置合适的尺寸
if os.name != 'nt' and 'ANDROID_ARGUMENT' in os.environ:
    # Android 设备
    ORIGINAL_WIDTH = 360
    ORIGINAL_HEIGHT = 640
    IS_MOBILE = True
else:
    # Windows/桌面设备
    ORIGINAL_WIDTH = 1400
    ORIGINAL_HEIGHT = 700
    IS_MOBILE = False

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
    """获取资源文件的正确路径"""
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
                    print(f"无法加载图片: {path}")
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
                print(f"无法加载背景图片: {self.background_image_path}")
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
        
        # 移动设备调整
        if IS_MOBILE:
            self.item_size = 40
            self.position = (10, 10)

    def add_item(self, item):
        if len(self.items) < self.max_items and not any(i.name == item.name for i in self.items):
            self.items.append(item)

# -------------------- 消息框 --------------------
class MessageBox:
    def __init__(self):
        self.visible = False
        self.item = None
        
        # 根据平台设置不同的大小
        if IS_MOBILE:
            self.rect = [ORIGINAL_WIDTH//2 - 150, ORIGINAL_HEIGHT//2 - 200, 300, 400]
        else:
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
    scale_x = NumericProperty(1.0)
    scale_y = NumericProperty(1.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 绑定尺寸变化事件
        self.bind(size=self.on_size_change)
        
        # 加载音效
        try:
            self.correct_sound = SoundLoader.load(resource_path("correct.mp3"))
            if self.correct_sound:
                print("音效加载成功")
            else:
                print("音效加载失败")
        except Exception as e:
            print(f"音效加载错误: {e}")
            self.correct_sound = None

        # 初始化场景
        self.scenes = [
            Scene("指挥室", resource_path("cabin.png")),
            Scene("船舱", resource_path("bridge.png"))
        ]

        # 根据平台设置不同的物品位置和大小
        if IS_MOBILE:
            # 移动设备配置
            self.scenes[0].add_item(Item("协议", "重要文件", (180, 250), "polygon", 
                                       hotspot_size=60,
                                       polygon_points=[(150, 220), (210, 220), (210, 280), (150, 280)], 
                                       image_paths=[resource_path("protocol.png")]))
            self.scenes[0].add_item(Item("指南针", "导航工具", (200, 350), "circle", 
                                       hotspot_size=40, 
                                       image_paths=[resource_path("zhinanzhen1.png"), resource_path("zhinanzhen2.png")]))
            self.scenes[1].add_item(Item("黄金", "贵重物品", (150, 200), "polygon", 
                                       hotspot_size=60,
                                       polygon_points=[(120, 170), (180, 170), (180, 230), (120, 230)], 
                                       image_paths=[resource_path("huangjin1.png"), resource_path("huangjin2.png")]))
        else:
            # 桌面设备配置
            self.scenes[0].add_item(Item("协议", "重要文件", (400, 420), "polygon", 
                                       hotspot_size=100,
                                       polygon_points=[(370, 400), (570, 400), (570, 440), (370, 440)], 
                                       image_paths=[resource_path("protocol.png")]))
            self.scenes[0].add_item(Item("指南针", "导航工具", (760, 520), "circle", 
                                       hotspot_size=70, 
                                       image_paths=[resource_path("zhinanzhen1.png"), resource_path("zhinanzhen2.png")]))
            self.scenes[1].add_item(Item("黄金", "贵重物品", (650, 360), "polygon", 
                                       hotspot_size=100,
                                       polygon_points=[(600, 330), (850, 330), (850, 390), (600, 390)], 
                                       image_paths=[resource_path("huangjin1.png"), resource_path("huangjin2.png")]))

        # 物品栏
        self.inventory = Inventory()

        # 消息框
        self.message_box = MessageBox()

        # 场景切换按钮
        if IS_MOBILE:
            self.next_button = Item("下一场景", "", (ORIGINAL_WIDTH-40, ORIGINAL_HEIGHT//2), "circle", hotspot_size=30)
            self.prev_button = Item("上一场景", "", (ORIGINAL_WIDTH-40, ORIGINAL_HEIGHT//2+50), "circle", hotspot_size=30)
        else:
            self.next_button = Item("下一场景", "", (ORIGINAL_WIDTH-60, ORIGINAL_HEIGHT//2), "circle", hotspot_size=50)
            self.prev_button = Item("上一场景", "", (ORIGINAL_WIDTH-60, ORIGINAL_HEIGHT//2+80), "circle", hotspot_size=50)

        # 更新帧
        Clock.schedule_interval(self.update, 1/60)
        
        print(f"游戏初始化完成，屏幕尺寸: {Window.size}")
        print(f"移动设备模式: {IS_MOBILE}")

    def on_size_change(self, instance, value):
        """当窗口大小改变时调整缩放比例"""
        if ORIGINAL_WIDTH > 0 and ORIGINAL_HEIGHT > 0:
            self.scale_x = self.width / ORIGINAL_WIDTH
            self.scale_y = self.height / ORIGINAL_HEIGHT
            print(f"缩放比例更新: scale_x={self.scale_x:.2f}, scale_y={self.scale_y:.2f}")

    def scale_position(self, pos):
        """缩放位置坐标"""
        x, y = pos
        return (x * self.scale_x, y * self.scale_y)
    
    def scale_size(self, size):
        """缩放大小的坐标"""
        w, h = size
        return (w * self.scale_x, h * self.scale_y)

    def next_scene(self):
        self.current_scene_index = (self.current_scene_index + 1) % len(self.scenes)

    def prev_scene(self):
        self.current_scene_index = (self.current_scene_index - 1) % len(self.scenes)

    def update(self, dt):
        self.canvas.clear()
        self.message_box.update()
        
        with self.canvas:
            # 绘制背景
            scene = self.scenes[self.current_scene_index]
            if scene.bg_texture:
                Rectangle(texture=scene.bg_texture, pos=(0, 0), size=self.size)
            else:
                Color(*DARK_WOOD)
                Rectangle(pos=(0, 0), size=self.size)

            # 绘制物品栏
            Color(1, 1, 1)  # 重置颜色为白色
            for idx, item in enumerate(self.inventory.items):
                if item.inventory_image:
                    x, y = self.scale_position(self.inventory.position)
                    item_w, item_h = self.scale_size((self.inventory.item_size, self.inventory.item_size))
                    current_y = y + idx * (item_h + self.inventory.spacing)
                    Rectangle(texture=item.inventory_image, 
                             pos=(x, current_y), 
                             size=(item_w, item_h))

            # 绘制场景切换按钮（简化显示）
            Color(0.3, 0.3, 0.8, 0.7)
            next_x, next_y = self.scale_position(self.next_button.position)
            next_size = self.scale_size((self.next_button.hotspot_size, self.next_button.hotspot_size))
            Ellipse(pos=(next_x - next_size[0]/2, next_y - next_size[1]/2), 
                   size=next_size)
                   
            prev_x, prev_y = self.scale_position(self.prev_button.position)
            prev_size = self.scale_size((self.prev_button.hotspot_size, self.prev_button.hotspot_size))
            Ellipse(pos=(prev_x - prev_size[0]/2, prev_y - prev_size[1]/2), 
                   size=prev_size)

            # 绘制消息框
            if self.message_box.visible and self.message_box.item and self.message_box.scale > 0.0:
                x, y, w, h = self.message_box.rect
                # 缩放消息框位置和大小
                sx, sy = self.scale_position((x, y))
                sw, sh = self.scale_size((w, h))
                
                # 应用动画缩放
                current_sw = sw * self.message_box.scale
                current_sh = sh * self.message_box.scale
                current_sx = sx + (sw - current_sw) / 2
                current_sy = sy + (sh - current_sh) / 2
                
                # 绘制消息框背景
                Color(0.1, 0.1, 0.1, 0.9)
                Rectangle(pos=(current_sx, current_sy), size=(current_sw, current_sh))
                
                # 绘制边框
                Color(*GOLD)
                Line(rectangle=(current_sx, current_sy, current_sw, current_sh), width=2)
                
                # 显示物品图片
                if self.message_box.item.images:
                    img = self.message_box.item.images[0]
                    iw = current_sw * 0.8
                    ih = current_sh * 0.8
                    ix = current_sx + (current_sw - iw) / 2
                    iy = current_sy + (current_sh - ih) / 2
                    
                    Color(1, 1, 1)
                    Rectangle(texture=img, pos=(ix, iy), size=(iw, ih))

    def on_touch_down(self, touch):
        # 缩放触摸位置到原始坐标
        if self.scale_x > 0 and self.scale_y > 0:
            scaled_touch_pos = (touch.x / self.scale_x, touch.y / self.scale_y)
        else:
            scaled_touch_pos = (touch.x, touch.y)
            
        scene = self.scenes[self.current_scene_index]

        # 检查消息框
        if self.message_box.visible:
            if self.message_box.state == "open":
                self.message_box.close()
            return True

        # 检查场景切换按钮
        if self.next_button.check_collision(scaled_touch_pos):
            self.next_scene()
            return True
        if self.prev_button.check_collision(scaled_touch_pos):
            self.prev_scene()
            return True

        # 检查物品拾取
        for item in scene.items:
            if item.check_collision(scaled_touch_pos):
                self.inventory.add_item(item)
                print(f"拾取物品: {item.name}")
                if self.correct_sound:
                    self.correct_sound.play()
                self.message_box.show(item)
                return True

        return super().on_touch_down(touch)

# -------------------- Kivy App --------------------
class MyGameApp(App):
    def build(self):
        return GameWidget()
    
    def on_pause(self):
        # 当应用暂停时（Android）
        return True
    
    def on_resume(self):
        # 当应用恢复时（Android）
        pass

# -------------------- 启动 --------------------
if __name__ == "__main__":
    MyGameApp().run()
