import pygame
import sys
import os
import math
from pygame.locals import *

def resource_path(relative_path):
    """获取资源的绝对路径。用于PyInstaller打包后定位资源文件。"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller会创建临时文件夹存储资源
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 初始化pygame
pygame.init()
pygame.mixer.init()     # 新增

# 原始设计尺寸
ORIGINAL_WIDTH = 1400
ORIGINAL_HEIGHT = 700

# 屏幕设置
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 700
# 修改
screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT), 
    pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE
)
pygame.display.set_caption("船舱探索")

# 颜色定义
DARK_WOOD = (50, 35, 25)
LIGHT_WOOD = (120, 90, 60)
PAPER = (250, 240, 220)
GOLD = (200, 170, 80)
BRASS = (180, 150, 60)
DARK_LEATHER = (50, 40, 30)
TEXT_COLOR = (220, 220, 210)
HIGHLIGHT = (220, 200, 100)
HOTSPOT_COLOR = (255, 255, 0, 100)
PANEL_COLOR = (40, 40, 40, 200)
BUTTON_COLOR = (100, 80, 60)
BUTTON_HOVER = (150, 120, 90)

# 字体
try:
    font = pygame.font.Font(resource_path("simhei.ttf"), 20)
    title_font = pygame.font.Font(resource_path("simhei.ttf"), 28)
    item_font = pygame.font.Font(resource_path("simhei.ttf"), 18)
except:
    font = pygame.font.SysFont('microsoftyahei', 20)
    title_font = pygame.font.SysFont('microsoftyahei', 28)
    item_font = pygame.font.SysFont('microsoftyahei', 18)

# 加载音效
try:
    correct_sound = pygame.mixer.Sound(resource_path("correct.mp3"))
    sound_available = True
except:
    print("无法加载音效文件 correct.mp3")
    sound_available = False

# 场景类
class Scene:
    def __init__(self, name, background_image=None):
        self.name = name
        self.items = []
        self.background_image_path = background_image
        self.background = None
        self.original_background = None  # 存储原始背景图片
        self.update_background()  # 初始化背景
        
    def update_background(self):
        """更新背景到当前屏幕尺寸"""
        if self.background_image_path:
            try:
                # 加载原始图片
                if self.original_background is None:
                    self.original_background = pygame.image.load(self.background_image_path)
                # 调整大小
                self.background = pygame.transform.scale(self.original_background, (screen.get_width() - 120, screen.get_height() - 20))
            except:
                print(f"无法加载背景图片: {self.background_image_path}")
                self.background = self.create_default_background()
        else:
            self.background = self.create_default_background()
    
    def create_default_background(self):
        background = pygame.Surface((screen.get_width() - 120, screen.get_height() - 20))
        background.fill(DARK_WOOD)
        
        # 绘制一些简单的装饰
        pygame.draw.rect(background, LIGHT_WOOD, (50, 50, background.get_width()-100, background.get_height()-100), border_radius=10)
        pygame.draw.rect(background, DARK_WOOD, (50, 50, background.get_width()-100, background.get_height()-100), 3, border_radius=10)
        
        # 显示场景名称
        text = title_font.render(self.name, True, GOLD)
        background.blit(text, (background.get_width()//2 - text.get_width()//2, 30))
        
        return background
    
    def add_item(self, item):
        self.items.append(item)
    
    def draw(self, surface, offset_x, offset_y):
        # 绘制背景
        surface.blit(self.background, (offset_x, offset_y))
        
        # 绘制物品热点区域
        # for item in self.items:
        #     item.draw_hotspot(surface, offset_x, offset_y)

# 物品类（修改为支持缩放）
class Item:
    def __init__(self, name, description, position, hotspot_shape="circle", hotspot_size=50, polygon_points=None, image_paths=None):
        self.name = name
        self.description = description
        self.position = position  # 原始位置（基于原始屏幕尺寸）
        self.hotspot_shape = hotspot_shape
        self.hotspot_size = hotspot_size  # 原始尺寸
        self.polygon_points = polygon_points or []  # 原始多边形点
        self.inventory_pos = None
        self.image_paths = image_paths or []  # 存储图片路径列表
        self.inventory_image = None  # 用于物品栏的图片
        
        # 计算缩放后的属性
        self.scaled_position = position
        self.scaled_hotspot_size = hotspot_size
        self.scaled_polygon_points = polygon_points or []
        self.scaled_rect = None
        
        self.update_scale()  # 初始化缩放
        
        # 加载并调整物品栏图片大小
        if self.image_paths:
            try:
                # 使用第一张图片作为物品栏图标
                img = pygame.image.load(self.image_paths[0])
                # 调整图片大小以适应物品栏
                self.inventory_image = pygame.transform.scale(img, (50, 50))
            except:
                print(f"无法加载物品栏图片: {self.image_paths[0]}")
                # 创建默认图片
                self.inventory_image = pygame.Surface((50, 50))
                self.inventory_image.fill((255, 0, 0))  # 红色表示加载失败
    
    def update_scale(self):
        """根据当前屏幕尺寸更新缩放后的属性"""
        # 计算缩放比例
        scale_x = screen.get_width() / ORIGINAL_WIDTH
        scale_y = screen.get_height() / ORIGINAL_HEIGHT
        
        # 更新缩放后的位置和尺寸
        self.scaled_position = (self.position[0] * scale_x, self.position[1] * scale_y)
        self.scaled_hotspot_size = self.hotspot_size * min(scale_x, scale_y)
        
        # 更新缩放后的多边形点
        self.scaled_polygon_points = [(p[0] * scale_x, p[1] * scale_y) for p in self.polygon_points]
        
        # 创建边界矩形用于快速检测
        if self.hotspot_shape == "circle":
            self.scaled_rect = pygame.Rect(
                self.scaled_position[0] - self.scaled_hotspot_size//2, 
                self.scaled_position[1] - self.scaled_hotspot_size//2, 
                self.scaled_hotspot_size, self.scaled_hotspot_size
            )
        elif self.hotspot_shape == "polygon" and self.scaled_polygon_points:
            # 计算多边形边界
            min_x = min(p[0] for p in self.scaled_polygon_points)
            max_x = max(p[0] for p in self.scaled_polygon_points)
            min_y = min(p[1] for p in self.scaled_polygon_points)
            max_y = max(p[1] for p in self.scaled_polygon_points)
            self.scaled_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
        else:
            # 默认使用圆形
            self.scaled_rect = pygame.Rect(
                self.scaled_position[0] - self.scaled_hotspot_size//2, 
                self.scaled_position[1] - self.scaled_hotspot_size//2, 
                self.scaled_hotspot_size, self.scaled_hotspot_size
            )
    
    def point_in_polygon(self, point, polygon_points):
        """检查点是否在多边形内（射线法）"""
        if not polygon_points:
            return False
            
        x, y = point
        n = len(polygon_points)
        inside = False
        
        p1x, p1y = polygon_points[0]
        for i in range(n + 1):
            p2x, p2y = polygon_points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
            
        return inside
    
    def check_collision(self, point):
        """检查点是否在热点区域内"""
        if not self.scaled_rect.collidepoint(point):
            return False
            
        if self.hotspot_shape == "circle":
            # 计算点到圆心的距离
            dx = point[0] - self.scaled_position[0]
            dy = point[1] - self.scaled_position[1]
            distance = math.sqrt(dx*dx + dy*dy)
            return distance <= self.scaled_hotspot_size/2
            
        elif self.hotspot_shape == "polygon":
            return self.point_in_polygon(point, self.scaled_polygon_points)
            
        return False
        
    def draw_hotspot(self, surface, offset_x, offset_y):
        """绘制热点区域（用于调试）"""
        if self.hotspot_shape == "circle":
            # 绘制圆形热点区域
            hotspot_surf = pygame.Surface((self.scaled_hotspot_size, self.scaled_hotspot_size), pygame.SRCALPHA)
            pygame.draw.circle(hotspot_surf, HOTSPOT_COLOR, 
                              (self.scaled_hotspot_size//2, self.scaled_hotspot_size//2), 
                              self.scaled_hotspot_size//2)
            surface.blit(hotspot_surf, (offset_x + self.scaled_rect.x, offset_y + self.scaled_rect.y))
            
        elif self.hotspot_shape == "polygon" and self.scaled_polygon_points:
            # 绘制多边形热点区域
            hotspot_surf = pygame.Surface((self.scaled_rect.width, self.scaled_rect.height), pygame.SRCALPHA)
            # 将多边形点转换到相对于边界矩形的位置
            relative_points = [(p[0] - self.scaled_rect.x, p[1] - self.scaled_rect.y) for p in self.scaled_polygon_points]
            pygame.draw.polygon(hotspot_surf, HOTSPOT_COLOR, relative_points)
            surface.blit(hotspot_surf, (offset_x + self.scaled_rect.x, offset_y + self.scaled_rect.y))

# 物品栏类（修改为紧密排列的九个垂直方形框）
class Inventory:
    def __init__(self):
        self.items = []
        self.position = (20, 40)  # 调整位置
        self.item_size = 60  # 减小尺寸
        self.spacing = 5  # 减小间距
        self.item_rects = {}  # 存储物品在物品栏中的位置
    
    def add_item(self, item):
        if not any(i.name == item.name for i in self.items):
            self.items.append(item)
    
    def draw(self, surface):
        # 计算起始位置
        start_x = self.position[0]
        start_y = self.position[1]
        
        # 绘制九个垂直排列的正方形框（紧密排列）
        self.item_rects.clear()  # 清空之前的矩形记录
        
        for i in range(9):
            rect_y = start_y + i * (self.item_size + self.spacing)
            
            rect = pygame.Rect(start_x, rect_y, self.item_size, self.item_size)
            
            # 绘制正方形框
            pygame.draw.rect(surface, DARK_LEATHER, rect, border_radius=5)
            pygame.draw.rect(surface, GOLD, rect, 2, border_radius=5)
            
            # 如果有物品，则显示物品
            if i < len(self.items):
                item = self.items[i]
                
                # 显示物品图片（如果有）
                if item.inventory_image:
                    # 计算图片位置（居中）
                    img_x = rect.x + (rect.width - item.inventory_image.get_width()) // 2
                    img_y = rect.y + (rect.height - item.inventory_image.get_height()) // 2
                    surface.blit(item.inventory_image, (img_x, img_y))
                
                # 存储位置用于点击检测
                self.item_rects[item] = rect
    
    def get_item_at_pos(self, mouse_pos):
        for item, rect in self.item_rects.items():
            if rect.collidepoint(mouse_pos):
                return item
        return None

# 消息框类（带缩放动画）- 修改为只显示图片，并统一图片大小
class MessageBox:
    def __init__(self):
        self.visible = False
        self.item = None
        # 放大消息框尺寸以更好地显示图片
        self.rect = pygame.Rect(screen.get_width()//2 - 400, screen.get_height()//2 - 300, 800, 600)
        self.close_rect = pygame.Rect(self.rect.right - 40, self.rect.top + 10, 30, 30)
        
        # 动画相关属性
        self.animation_state = "closed"  # closed, opening, open, closing
        self.animation_progress = 0.0  # 0.0 to 1.0
        self.animation_speed = 0.15  # 每帧动画进度变化量（稍微减慢以获得更平滑的效果）
        
        # 图片缓存
        self.image_cache = {}
        
        # 统一图片尺寸
        self.image_width = 700  # 统一图片宽度
        self.image_height = 250  # 降低图片高度，为两张图片留出空间
        
    def ease_out_back(self, x):
        """缓动函数：easeOutBack，提供更自然的动画效果"""
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * pow(x - 1, 3) + c1 * pow(x - 1, 2)
    
    def show(self, item):
        self.item = item
        self.visible = True
        self.animation_state = "opening"
        self.animation_progress = 0.0
        
        # 预加载图片
        if self.item.image_paths:
            for path in self.item.image_paths:
                if path not in self.image_cache:
                    try:
                        img = pygame.image.load(path)
                        # 统一调整图片大小
                        img = self.scale_image(img, self.image_width, self.image_height)
                        self.image_cache[path] = img
                    except:
                        print(f"无法加载图片: {path}")
                        # 创建默认图片
                        default_img = pygame.Surface((self.image_width, self.image_height))
                        default_img.fill((255, 0, 0))  # 红色表示加载失败
                        self.image_cache[path] = default_img
        
    def scale_image(self, img, width, height):
        """缩放图片到统一尺寸，保持宽高比并添加背景"""
        # 创建目标表面
        target_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        target_surface.fill((0, 0, 0, 0))  # 透明背景
        
        # 计算缩放比例
        img_width, img_height = img.get_size()
        ratio = min(width / img_width, height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        # 缩放图片
        scaled_img = pygame.transform.smoothscale(img, (new_width, new_height))
        
        # 居中放置图片
        x = (width - new_width) // 2
        y = (height - new_height) // 2
        target_surface.blit(scaled_img, (x, y))
        
        return target_surface
        
    def close(self):
        self.animation_state = "closing"
        self.animation_progress = 1.0
        
    def update_animation(self):
        if self.animation_state == "opening":
            self.animation_progress += self.animation_speed
            if self.animation_progress >= 1.0:
                self.animation_progress = 1.0
                self.animation_state = "open"
                
        elif self.animation_state == "closing":
            self.animation_progress -= self.animation_speed
            if self.animation_progress <= 0.0:
                self.animation_progress = 0.0
                self.animation_state = "closed"
                self.visible = False
                self.item = None
    
    def draw(self, surface):
        if self.animation_state == "closed":
            return
            
        # 使用缓动函数计算当前缩放比例
        scale = self.ease_out_back(self.animation_progress)
        
        # 计算当前矩形大小和位置
        current_width = int(self.rect.width * scale)
        current_height = int(self.rect.height * scale)
        current_x = self.rect.centerx - current_width // 2
        current_y = self.rect.centery - current_height // 2
        current_rect = pygame.Rect(current_x, current_y, current_width, current_height)
        
        # 计算透明度（0-255）
        alpha = int(255 * self.animation_progress)
        
        # 创建临时表面用于绘制消息框内容
        temp_surface = pygame.Surface((current_width, current_height), pygame.SRCALPHA)
        
        # 绘制消息框背景（带透明度）
        bg_color = PANEL_COLOR[:3] + (int(PANEL_COLOR[3] * self.animation_progress),)
        pygame.draw.rect(temp_surface, bg_color, (0, 0, current_width, current_height), border_radius=int(20 * scale))
        pygame.draw.rect(temp_surface, BRASS, (0, 0, current_width, current_height), int(3 * scale), border_radius=int(20 * scale))
        
        # 计算关闭按钮位置
        close_btn_size = int(30 * scale)
        close_btn_x = current_width - close_btn_size - int(10 * scale)
        close_btn_y = int(10 * scale)
        close_btn_rect = pygame.Rect(close_btn_x, close_btn_y, close_btn_size, close_btn_size)
        
        if scale > 0.5:  # 当缩放比例足够大时才显示内容
            # 绘制图片
            if self.item.image_paths:
                # 计算图片区域的总高度
                total_img_height = len(self.item.image_paths) * self.image_height
                if len(self.item.image_paths) > 1:
                    total_img_height += (len(self.item.image_paths) - 1) * 10  # 减小图片间距
                
                # 图片的起始y坐标（从消息框顶部向下偏移100像素）
                img_y = int(100 * scale)
                
                for img_path in self.item.image_paths:
                    if img_path in self.image_cache:
                        img = self.image_cache[img_path]
                        # 根据缩放比例调整图片大小
                        img_width = int(img.get_width() * scale)
                        img_height = int(img.get_height() * scale)
                        scaled_img = pygame.transform.smoothscale(img, (img_width, img_height))
                        
                        img_x = (current_width - img_width) // 2
                        temp_surface.blit(scaled_img, (img_x, img_y))
                        img_y += img_height - int(30 * scale)  # 减小图片间距
            
            # 关闭按钮
            pygame.draw.rect(temp_surface, BRASS, close_btn_rect, border_radius=int(5 * scale))
            pygame.draw.rect(temp_surface, DARK_LEATHER, close_btn_rect, int(2 * scale), border_radius=int(5 * scale))
            close_text = font.render("X", True, DARK_LEATHER)
            close_rect = close_text.get_rect(center=close_btn_rect.center)
            temp_surface.blit(close_text, close_rect)
            
            # 存储当前关闭按钮位置用于点击检测
            self.close_rect = pygame.Rect(
                current_x + close_btn_x,
                current_y + close_btn_y,
                close_btn_size,
                close_btn_size
            )
        
        # 设置临时表面的透明度
        temp_surface.set_alpha(alpha)
        
        # 将临时表面绘制到屏幕上
        surface.blit(temp_surface, (current_x, current_y))

# 创建场景
scenes = [
    Scene("指挥室", resource_path("cabin.png")),
    Scene("船舱", resource_path("bridge.png"))
]

# 为指挥室场景添加物品（使用不规则多边形定义点击区域）
# 协议 - 矩形区域
protocol_points = [
    (370, 400), (570, 400), (570, 440), (370, 440)
]
scenes[0].add_item(Item("协议", "", (400, 420), "polygon", polygon_points=protocol_points, 
                        image_paths=[resource_path("protocol.png")]))

# 指南针 - 圆形区域（保留原有方式）
scenes[0].add_item(Item("指南针", "", (760, 520), "circle", hotspot_size=70, 
                        image_paths=[resource_path("zhinanzhen1.png"), resource_path("zhinanzhen2.png")]))

# 航线示意图
route_points = [
    (1080, 50), (630, 50), (630, 300), (1080, 300)
]
scenes[0].add_item(Item("迪亚士、哥伦布、达伽马航线示意图", "", (600, 200), "polygon", 
                        polygon_points=route_points, 
                        image_paths=[resource_path("hangxian1.png"), resource_path("hangxian2.png")]))

# 世界地图 - 不规则多边形
map_points = [
    (940, 480), (1220, 420), (1220, 600), (1000, 630), (940, 540)
]
scenes[0].add_item(Item("托勒密世界地图", "", (850, 520), "polygon", polygon_points=map_points, 
                        image_paths=[resource_path("ditu.png"), resource_path("ditu2.png")]))

# 马可波罗行纪 - 五边形
book_points = [
    (820, 460), (920, 460), (920, 560), (820, 560)
]
scenes[0].add_item(Item("马可波罗行纪", "激发了欧洲人对东方的无限想象和向往", (700, 520), "polygon", 
                        polygon_points=book_points, 
                        image_paths=[resource_path("make.png"), resource_path("make2.png")]))

# 为船舱场景添加物品 - 黄金
gold_points = [
    (600, 330), (850, 330), (850, 390), (600, 390)
]
scenes[1].add_item(Item("黄金", "巨大的木质舵轮，用于控制船只的航行方向", (200, 200), "polygon", 
                        polygon_points=gold_points, 
                        image_paths=[resource_path("huangjin1.png"), resource_path("huangjin2.png")]))

# 皮加费塔讲述
human_points = [
    (830, 50), (1000, 50), (1000, 400), (830, 400)
]
scenes[1].add_item(Item("皮加费塔讲述", "巨大的木质舵轮，用于控制船只的航行方向", (200, 200), "polygon", 
                        polygon_points=human_points, 
                        image_paths=[resource_path("jiangshu.png")]))

# 香料
xiangliao_points = [
    (40, 500), (230, 500), (230, 700), (40, 700)
]
scenes[1].add_item(Item("香料", "巨大的木质舵轮，用于控制船只的航行方向", (200, 200), "polygon", 
                        polygon_points=xiangliao_points, 
                        image_paths=[resource_path("xiangliao1.png"), resource_path("xiangliao2.png")]))

# 船舱
chauncang_points = [
    (1100, 50), (1300, 50), (1300, 400), (1100, 400)
]
scenes[1].add_item(Item("船舱", "巨大的木质舵轮，用于控制船只的航行方向", (200, 200), "polygon", 
                        polygon_points=chauncang_points, 
                        image_paths=[resource_path("chuan1.png"), resource_path("chuan2.png")]))

# 创建物品栏
inventory = Inventory()

# 创建消息框
message_box = MessageBox()

# 创建场景切换按钮 - 使用原始设计尺寸的位置
next_button_item = Item("下一场景", "", (ORIGINAL_WIDTH - 60, ORIGINAL_HEIGHT // 2), "circle", hotspot_size=50)
prev_button_item = Item("上一场景", "", (ORIGINAL_WIDTH - 60, ORIGINAL_HEIGHT // 2 + 80), "circle", hotspot_size=50)

# 主循环
clock = pygame.time.Clock()
running = True
current_scene_index = 0

def next_scene():
    global current_scene_index
    current_scene_index = (current_scene_index + 1) % len(scenes)

def prev_scene():
    global current_scene_index
    current_scene_index = (current_scene_index - 1) % len(scenes)

# 修改
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    # 更新所有物品的缩放
    for scene in scenes:
        for item in scene.items:
            item.update_scale()
    
    # 更新切换按钮的缩放
    next_button_item.update_scale()
    prev_button_item.update_scale()
    
    # 更新消息框动画
    message_box.update_animation()
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            
        elif event.type == VIDEORESIZE:
            # 更新所有场景的背景
            for scene in scenes:
                scene.update_background()
        # 更新消息框位置
        message_box.rect = pygame.Rect(screen.get_width()//2 - 400, screen.get_height()//2 - 300, 800, 600)
            
        # 处理触摸和鼠标点击事件
        if event.type in (MOUSEBUTTONDOWN, pygame.FINGERDOWN, pygame.MOUSEBUTTONUP):
            # 将触摸事件转换为鼠标事件坐标
            if event.type == pygame.FINGERDOWN:
                # 转换触摸坐标到屏幕坐标
                x = event.x * screen.get_width()
                y = event.y * screen.get_height()
                event_pos = (x, y)
                
                # 检查是否点击了场景切换按钮
                if next_button_item.check_collision(event_pos):
                    next_scene()
                    continue
                    
                if prev_button_item.check_collision(event_pos):
                    prev_scene()
                    continue
                
                # 检查是否点击了关闭按钮
                if message_box.animation_state in ["open", "opening"] and message_box.close_rect.collidepoint(event_pos):
                    message_box.close()
                    continue
                
                # 检查是否点击了场景中的物品热点
                if message_box.animation_state == "closed":
                    # 使用与绘制相同的偏移量 (100, 10)
                    scene_rect = pygame.Rect(100, 10, screen.get_width() - 210, screen.get_height() - 20)
                    if scene_rect.collidepoint(event_pos):
                        # 转换为场景内的坐标
                        scene_x = event_pos[0] - 100
                        scene_y = event_pos[1] - 10
                        
                        current_scene = scenes[current_scene_index]
                        for item in current_scene.items:
                            if item.check_collision((scene_x, scene_y)):
                                # 添加物品到物品栏
                                if not any(i.name == item.name for i in inventory.items):
                                    inventory.add_item(item)
                                
                                # 播放音效
                                if sound_available:
                                    correct_sound.play()
                                
                                # 显示消息框
                                message_box.show(item)
                                break
                
                # 检查是否点击了物品栏中的物品
                clicked_item = inventory.get_item_at_pos(event_pos)
                if clicked_item:
                    message_box.show(clicked_item)
            elif event.type == pygame.MOUSEBUTTONUP:
                # 处理鼠标释放事件（触摸屏可能使用这个事件）
                event_pos = event.pos
            else:
                event_pos = event.pos
            
            # 检查是否点击了关闭按钮
            if message_box.animation_state in ["open", "opening"] and message_box.close_rect.collidepoint(event_pos):
                message_box.close()
                continue
            
            # 检查是否点击了场景切换按钮
            if next_button_item.check_collision(event_pos):
                next_scene()
                continue
                
            if prev_button_item.check_collision(event_pos):
                prev_scene()
                continue
            
            # 检查是否点击了场景中的物品热点
            if message_box.animation_state == "closed":
                # 使用与绘制相同的偏移量 (100, 10)
                scene_rect = pygame.Rect(100, 10, screen.get_width() - 210, screen.get_height() - 20)
                if scene_rect.collidepoint(event_pos):
                    # 转换为场景内的坐标
                    scene_x = event_pos[0] - 100
                    scene_y = event_pos[1] - 10
                    
                    current_scene = scenes[current_scene_index]
                    for item in current_scene.items:
                        if item.check_collision((scene_x, scene_y)):
                            # 添加物品到物品栏
                            if not any(i.name == item.name for i in inventory.items):
                                inventory.add_item(item)
                            
                            # 播放音效
                            if sound_available:
                                correct_sound.play()
                            
                            # 显示消息框
                            message_box.show(item)
                            break
            
            # 检查是否点击了物品栏中的物品
            clicked_item = inventory.get_item_at_pos(event_pos)
            if clicked_item:
                message_box.show(clicked_item)
    
    # 绘制界面
    screen.fill(DARK_WOOD)
    
    # 绘制当前场景
    current_scene = scenes[current_scene_index]
    current_scene.draw(screen, 100, 10)
    
    # 绘制物品栏（九个紧密排列的方形框）
    inventory.draw(screen)
    
    # 绘制场景切换按钮（作为圆形热点）
    pygame.draw.circle(screen, BUTTON_COLOR, next_button_item.scaled_position, next_button_item.scaled_hotspot_size//2)
    pygame.draw.circle(screen, GOLD, next_button_item.scaled_position, next_button_item.scaled_hotspot_size//2, 2)
    next_text = font.render("→", True, TEXT_COLOR)
    screen.blit(next_text, (next_button_item.scaled_position[0] - next_text.get_width()//2, 
                           next_button_item.scaled_position[1] - next_text.get_height()//2))
    
    pygame.draw.circle(screen, BUTTON_COLOR, prev_button_item.scaled_position, prev_button_item.scaled_hotspot_size//2)
    pygame.draw.circle(screen, GOLD, prev_button_item.scaled_position, prev_button_item.scaled_hotspot_size//2, 2)
    prev_text = font.render("←", True, TEXT_COLOR)
    screen.blit(prev_text, (prev_button_item.scaled_position[0] - prev_text.get_width()//2, 
                           prev_button_item.scaled_position[1] - prev_text.get_height()//2))
    
    # 绘制消息框
    message_box.draw(screen)
    
    # 绘制场景名称（右下角）
    scene_name = font.render(f"场景: {current_scene.name}", True, TEXT_COLOR)
    screen.blit(scene_name, (screen.get_width() - scene_name.get_width() - 120, screen.get_height() - 40))

    
    pygame.display.flip()
    clock.tick(60)  # 保持60FPS以获得流畅动画

pygame.quit()
sys.exit()