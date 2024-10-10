from seleniumbase import Driver

driver = Driver(uc=True)
driver.get("https://www.g2.com/categories/video")
driver.sleep(3)
driver.quit()
