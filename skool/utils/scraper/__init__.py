from selenium_driverless import webdriver
import os
import shutil


def setup_temp_profile():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir_abspath = os.path.abspath(current_dir)
    root_dir = os.path.join(current_dir_abspath, "..", "..")
    root_dir_abspath = os.path.abspath(root_dir)

    profiles_dir = os.path.join(root_dir_abspath, "utils", "profiles")
    temp_dir = os.path.join(root_dir_abspath, "profiles_temp")
    temp_dir_abspath = os.path.abspath(temp_dir)

    profile_name = "Profile 2"

    if os.path.exists(temp_dir_abspath):
        try:
            shutil.rmtree(temp_dir_abspath)
            print("Temp folder successfully removed.")
        except Exception as e:
            print(f"Error removing temp folder: {e}")

    os.makedirs(temp_dir_abspath, exist_ok=True)

    source_profile = os.path.join(profiles_dir, profile_name)
    dest_profile = os.path.join(temp_dir_abspath, profile_name)

    if os.path.exists(dest_profile):
        shutil.rmtree(dest_profile)

    shutil.copytree(source_profile, dest_profile)
    return temp_dir_abspath, profile_name


async def start_driver():
    temp_dir_abspath, profile_name = setup_temp_profile()

    options = webdriver.ChromeOptions()
    options.user_data_dir = temp_dir_abspath
    options.add_argument(f"--user-data-dir={temp_dir_abspath}")
    options.add_argument(f"--profile-directory={profile_name}")
    # options.add_argument("--headless")   # uncomment this line to run in headless mode
    # options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-translate")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    options.add_argument("--disable-features=BlockInsecurePrivateNetworkRequests")
    options.add_argument("--disable-features=OutOfBlinkCors")
    options.add_argument("--disable-features=SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure")
    options.add_argument("--disable-features=CrossSiteDocumentBlockingIfIsolating,CrossSiteDocumentBlockingAlways")
    options.add_argument("--disable-features=ImprovedCookieControls,LaxSameSiteCookies,SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure")
    options.add_argument("--disable-features=SameSiteDefaultChecksMethodRigorously")
    driver = await webdriver.Chrome(options=options)
    return driver


async def get_element_details(driver, element):
    attributes = await driver.execute_script(
        """
          var items = {};
          for (index = 0; index < arguments[0].attributes.length; ++index) {
              items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value
          };
          return items;
        """,
        element,
    )

    properties = await driver.execute_script(
        """
          var props = {};
          var element = arguments[0];
          props['tagName'] = element.tagName;
          props['text'] = element.textContent;
          props['isDisplayed'] = element.offsetParent !== null;
          props['isEnabled'] = !element.disabled;
          return props;
        """,
        element,
    )

    details = {**attributes, **properties}
    return details
