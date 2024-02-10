import time
from core import color, picture


def to_mail(self):
    img_possibles = {"main_page_home-feature": (1141, 43)}
    img_ends = "mail_menu"
    picture.co_detect(self, None, None, img_ends, img_possibles, True)


def implement(self):
    self.quick_method_to_main_page()
    to_mail(self)
    if color.judge_rgb_range(self, 1142, 646, 206, 226, 207, 227, 208, 228):
        self.logger.info("mail reward HAS BEEN COLLECTED, quit")
        self.click(1236, 39, wait=False)
    elif color.judge_rgb_range(self, 1142, 646, 235, 255, 233, 243, 65, 85):
        self.logger.info("COLLECT mail reward")
        time.sleep(0.5)
        self.click(1142, 670, duration=2, wait_over=True)
    else:
        self.logger.info("Can't detect button")
        self.click(1236, 39, wait=False)
        return False
    return True
