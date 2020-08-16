import winsound
import glob
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def start_driver():
    driver = webdriver.Chrome()
    driver.set_page_load_timeout(5000000)
    
    # throttle
    driver.set_network_conditions(
    offline=False,
    latency=0,  # additional latency (ms)
    download_throughput=5000 * 1024,  # maximal throughput
    upload_throughput=5000 * 1024)  # maximal throughput
    return driver
    
def benchmark(method, dataset, firstid, commonfield):
    base_url = "http://127.0.0.1:5000/"
    flask_address = base_url + "collections"

    flask_urls = [f"{flask_address}/{dataset}/visualise/{method}",
          f"{flask_address}/{dataset}/0/edit/attributes/id/append/1/{method}",
          f"{flask_address}/{dataset}/all/edit/attributes/id/append/1/{method}",
          f"{flask_address}/{dataset}/index/0/{method}",
          f"{flask_address}/{dataset}/query/{commonfield}/%20/{method}",
          f"{flask_address}/{dataset}/heighten/{firstid}/{method}",
          f"{flask_address}/{dataset}/heighten/all/{method}",
          f"{flask_address}/{dataset}/buffer/0/{method}",
          f"{flask_address}/{dataset}/buffer/all/{method}"
          #f"{flask_address}/{dataset}/decode/{method}"
          ]

    
    tasks = ["visualise", "editone", "editall", "queryone", "queryall", "editgeomone", "editgeomall", "bufferone", "bufferall"]
    
    
    test_i = 10
    
    for t, url in enumerate(flask_urls):       
        task = tasks[t]
        print(url)
        print(task)
        
        
        for i in range(test_i):
            driver = start_driver()
        
            print(i)
            driver.get(url)
            try:
                element = WebDriverWait(driver, 5000000).until(
                        EC.alert_is_present(), task)
                alert = driver.switch_to.alert
                alert.accept()
                time.sleep(0.5)
                driver.close()
                    
            except:
                frequency = 1000
                duration = 750
                winsound.Beep(frequency, duration)
                break
            
            
    driver = start_driver()
    # create report
    driver.get(base_url + "report")
    time.sleep(1)
    driver.close()


methods = ["draco", "originalzlib", "dracozlib", "originalcbor", "dracocbor", "originalcborzlib", "dracocborzlib", 
                  "originalreplace", "dracoreplace", "originalcborreplace", "dracocborreplace", "originalcborreplacezlib", "dracocborreplacezlib"]

for method in methods:
    method = method

    cmpath = "../datasets/" + "original" + "/"
    files = glob.glob(cmpath + '*.json')
    f = open("benchmark_info.json", "r")
    paths = json.load(f)
    
    for file in files:
        dataset = file.split('\\')[-1].split('.')[0]

        if "_" in dataset:
            # if testing _noattr
            dataset = dataset.split("_")[0] + "_" + dataset.split("_")[1]
        
        firstid = paths[dataset]["firstid"]
        commonfield = paths[dataset]["commonfield"]
        
        benchmark(method, dataset, firstid, commonfield)