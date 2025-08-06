import time
from PIL import Image, ImageDraw

from .icons import carriage_icon_path, moon_icon_path
from .fonts import create_font
from .gray_scale import WHITE, DARK_GRAY, BLACK, LIGHT_GRAY
from .size_data import get_size_for_week


class ScreenUI:
    ICON_SIZE = 20
    ICON_CIRCLE_SIZE = 40
    ICON_X_MARGIN = 8
    PROGRESS_BAR_Y_CENTER = 105
    PROGRESS_BAR_HEIGHT = 10
    TEXT_MARGIN_TOP = 16
    TEXT_MARGIN_BOTTOM = 16
    TITLE_MARGIN_TOP = 8
    PAGE_DOTS_MARGIN_BOTTOM = 8
    PAGE_DOT_SIZE = 6
    PAGE_DOT_SPACING = 12

    def __init__(self, width, height, pregnancy, force_screen=None):
        self.pregnancy = pregnancy
        self.width = width
        self.height = height
        self.force_screen = force_screen  # For testing: 0=progress, 1=size, None=auto
        self._img = Image.new('L', (self.width, self.height), 255)  # 255: clear the frame
        self._img_draw = ImageDraw.Draw(self._img)

    def _calculate_text_size(self, message, font):
        _, _, w, h = self._img_draw.textbbox((0, 0), message, font=font)
        return w, h

    def _draw_title(self):
        font = create_font(20)
        title_str = "New Foley Tracker"
        w, h = self._calculate_text_size(title_str, font)
        pos = ((self.width-w)/2, self.TITLE_MARGIN_TOP)
        self._img_draw.text(pos, title_str, font=font, fill=BLACK)

    def _draw_percent(self):
        font = create_font(36)
        percent_str = self.pregnancy.get_percent_str()
        w, h = self._calculate_text_size(percent_str, font)
        title_font = create_font(20)
        _, title_h = self._calculate_text_size("New Foley Progress", title_font)
        pos = ((self.width-w)/2, self.TITLE_MARGIN_TOP + title_h + 8)
        self._img_draw.text(pos, percent_str, font=font, fill=BLACK)

    def _draw_weekday(self):
        font = create_font(30)
        percent_str = self.pregnancy.get_weekday_str()
        w, h = self._calculate_text_size(percent_str, font)
        pos = ((self.width-w)/2, (self.height-h-self.TEXT_MARGIN_BOTTOM))
        self._img_draw.text(pos, percent_str, font=font, fill=BLACK)

    def _draw_carriage(self):
        carriage = Image.open(carriage_icon_path)
        carriage.convert("1")
        circle_y1 = int(self.PROGRESS_BAR_Y_CENTER - self.ICON_CIRCLE_SIZE/2)
        circle_y2 = circle_y1 + self.ICON_CIRCLE_SIZE
        circle_x1 = self.width - self.ICON_CIRCLE_SIZE - self.ICON_X_MARGIN
        circle_x2 = self.width - self.ICON_X_MARGIN
        self._img_draw.ellipse((circle_x1, circle_y1, circle_x2, circle_y2), fill=DARK_GRAY)

        icon_x = int(circle_x1 + (self.ICON_CIRCLE_SIZE - carriage.width)/2)
        icon_y = int(circle_y1 + (self.ICON_CIRCLE_SIZE - carriage.height)/2)
        self._img.paste(carriage, (icon_x, icon_y), carriage)

    def _draw_moon(self):
        moon = Image.open(moon_icon_path)
        moon.convert("1")
        circle_y1 = int(self.PROGRESS_BAR_Y_CENTER - self.ICON_CIRCLE_SIZE/2)
        circle_y2 = circle_y1 + self.ICON_CIRCLE_SIZE
        circle_x1 = self.ICON_X_MARGIN
        circle_x2 = circle_x1 + self.ICON_CIRCLE_SIZE
        self._img_draw.ellipse((circle_x1, circle_y1, circle_x2, circle_y2), fill=LIGHT_GRAY)

        icon_x = int(circle_x1 + (self.ICON_CIRCLE_SIZE - moon.width)/2)
        icon_y = int(circle_y1 + (self.ICON_CIRCLE_SIZE - moon.height)/2)
        self._img.paste(moon, (icon_x, icon_y), moon)

    def _draw_progress_bar_mid(self):
        self._draw_progress_done()
        self._draw_progress_remaining()
        self._draw_progress_circle()

    def _draw_progress_bar(self):
        self._draw_moon()
        self._draw_progress_bar_mid()
        self._draw_carriage()

    def _get_current_screen(self):
        """Determine which screen to show based on time (switches every 5 minutes)"""
        if self.force_screen is not None:
            return self.force_screen
        current_minute = int(time.time() / 60)
        screen_index = (current_minute // 5) % 2
        return screen_index

    def _draw_size_comparison(self):
        """Draw the size comparison screen with two-column layout"""
        week = self.pregnancy.get_pregnancy_week()
        size_comparison, size_length = get_size_for_week(week)
        
        title_font = create_font(20)
        _, title_h = self._calculate_text_size("New Foley Progress", title_font)
        
        # Draw decorative line under title
        line_y = self.TITLE_MARGIN_TOP + title_h + 6
        self._img_draw.line([(20, line_y), (self.width - 20, line_y)], fill=LIGHT_GRAY, width=1)
        
        # Define column positions
        left_column_x = self.width * 0.25  # 25% from left
        right_column_x = self.width * 0.75  # 75% from left
        content_start_y = line_y + 20
        
        # LEFT COLUMN - Week information
        # Draw week label (smaller, gray)
        week_label_font = create_font(14)
        week_label = "WEEK"
        w, h = self._calculate_text_size(week_label, week_label_font)
        pos = (left_column_x - w/2, content_start_y)
        self._img_draw.text(pos, week_label, font=week_label_font, fill=DARK_GRAY)
        
        # Draw week number (large, bold)
        week_num_font = create_font(54)
        week_num_str = str(week)
        w, h = self._calculate_text_size(week_num_str, week_num_font)
        pos = (left_column_x - w/2, content_start_y + 20)
        self._img_draw.text(pos, week_num_str, font=week_num_font, fill=BLACK)
        
        # Draw vertical divider line
        divider_x = self.width / 2
        self._img_draw.line(
            [(divider_x, content_start_y), (divider_x, content_start_y + 80)], 
            fill=LIGHT_GRAY, 
            width=1
        )
        
        # RIGHT COLUMN - Size information
        # Draw "Baby size" label
        size_label_font = create_font(11)
        size_label = "BABY SIZE"
        w, h = self._calculate_text_size(size_label, size_label_font)
        pos = (right_column_x - w/2, content_start_y)
        self._img_draw.text(pos, size_label, font=size_label_font, fill=DARK_GRAY)
        
        # Draw size comparison
        size_str = size_comparison.upper()
        
        # Dynamically adjust font size based on text length
        if len(size_str) > 14:
            size_font = create_font(14)  # Smaller for very long names
        elif len(size_str) > 10:
            size_font = create_font(16)  # Medium for long names
        else:
            size_font = create_font(18)  # Normal size for short names
        
        # Check if we need to break into two lines
        w, h = self._calculate_text_size(size_str, size_font)
        max_width = (self.width / 2) - 20  # Maximum width for right column
        
        if w > max_width and ' ' in size_comparison:
            # Break into two lines
            words = size_comparison.split()
            if len(words) == 2:
                line1 = words[0].upper()
                line2 = words[1].upper()
            else:
                mid = len(words) // 2
                line1 = ' '.join(words[:mid]).upper()
                line2 = ' '.join(words[mid:]).upper()
            
            w1, h1 = self._calculate_text_size(line1, size_font)
            w2, h2 = self._calculate_text_size(line2, size_font)
            
            pos1 = (right_column_x - w1/2, content_start_y + 20)
            pos2 = (right_column_x - w2/2, content_start_y + 36)
            
            self._img_draw.text(pos1, line1, font=size_font, fill=BLACK)
            self._img_draw.text(pos2, line2, font=size_font, fill=BLACK)
            
            length_y = content_start_y + 56
        else:
            # Single line
            w, h = self._calculate_text_size(size_str, size_font)
            pos = (right_column_x - w/2, content_start_y + 28)
            self._img_draw.text(pos, size_str, font=size_font, fill=BLACK)
            length_y = content_start_y + 50
        
        # Draw length
        length_font = create_font(14)
        w, h = self._calculate_text_size(size_length, length_font)
        pos = (right_column_x - w/2, length_y)
        self._img_draw.text(pos, size_length, font=length_font, fill=DARK_GRAY)

    def _draw_page_indicators(self, current_page):
        """Draw page indicator dots at the bottom"""
        num_pages = 2
        dot_total_width = (num_pages - 1) * self.PAGE_DOT_SPACING + num_pages * self.PAGE_DOT_SIZE
        start_x = (self.width - dot_total_width) / 2
        y = self.height - self.PAGE_DOTS_MARGIN_BOTTOM - self.PAGE_DOT_SIZE
        
        for i in range(num_pages):
            x = start_x + i * (self.PAGE_DOT_SIZE + self.PAGE_DOT_SPACING)
            fill_color = BLACK if i == current_page else LIGHT_GRAY
            self._img_draw.ellipse(
                (x, y, x + self.PAGE_DOT_SIZE, y + self.PAGE_DOT_SIZE),
                fill=fill_color
            )

    def draw(self):
        # Clear the image to ensure no overlap
        self._img = Image.new('L', (self.width, self.height), 255)
        self._img_draw = ImageDraw.Draw(self._img)
        
        self._draw_title()
        
        current_screen = self._get_current_screen()
        
        if current_screen == 0:
            # Progress screen
            self._draw_percent()
            self._draw_weekday()
            self._draw_progress_bar()
        else:
            # Size comparison screen
            self._draw_size_comparison()
        
        self._draw_page_indicators(current_screen)
        return self._img

    def _draw_progress_done(self):
        y1 = int(self.PROGRESS_BAR_Y_CENTER - self.PROGRESS_BAR_HEIGHT/2)
        y2 = y1 + self.PROGRESS_BAR_HEIGHT
        x1 = self.ICON_X_MARGIN + self.ICON_CIRCLE_SIZE
        x2 = self._get_progress_bar_mid_x_point()
        self._img_draw.rectangle((x1, y1, x2, y2), fill=LIGHT_GRAY)

    def _draw_progress_remaining(self):
        y1 = int(self.PROGRESS_BAR_Y_CENTER - self.PROGRESS_BAR_HEIGHT/2)
        y2 = y1 + self.PROGRESS_BAR_HEIGHT
        x1 = self._get_progress_bar_mid_x_point()
        x2 = self.width - self.ICON_X_MARGIN - self.ICON_CIRCLE_SIZE
        self._img_draw.rectangle((x1, y1, x2, y2), fill=DARK_GRAY)

    def _draw_progress_circle(self):
        mid_x = self._get_progress_bar_mid_x_point()
        mid_y = self.PROGRESS_BAR_Y_CENTER
        size = self.PROGRESS_BAR_HEIGHT
        pos = (mid_x-size/2, mid_y-size/2, mid_x+size/2, mid_y+size/2)
        self._img_draw.ellipse(pos, fill=LIGHT_GRAY)

    def _get_progress_bar_length(self):
        return self.width - 2*self.ICON_X_MARGIN - 2*self.ICON_CIRCLE_SIZE

    def _get_progress_bar_mid_x_point(self):
        offset = self.ICON_X_MARGIN + self.ICON_CIRCLE_SIZE
        return offset + self._get_progress_bar_length()*self.pregnancy.get_progress()