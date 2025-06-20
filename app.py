from flask import Flask, render_template, request
import requests
from collections import defaultdict

app = Flask(__name__)

def GetCrimeData():
    url = "https://data.taipei/api/v1/dataset/adf80a2b-b29d-4fca-888c-bcd26ae314e0"
    params = {
        "scope": "resourceAquire",
        "resource_id": "adf80a2b-b29d-4fca-888c-bcd26ae314e0",
        "limit": 1000,
        "offset": 0
    }
    data = []
    try:
        while True:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                print(f"API error: Status code {response.status_code}")
                break
            json_data = response.json()
            if "result" not in json_data or "results" not in json_data["result"]:
                print("API error: Invalid response structure")
                break
            results = json_data["result"]["results"]
            if not results:
                break
            data.extend(results)
            params["offset"] += params["limit"]
        return data
    except Exception as e:
        print(f"API fetch error: {str(e)}")
        return []

def GetYear(record):
    date_field = record.get('發生日期', '')
    try:
        date_str = str(date_field)
        if len(date_str) >= 7 and date_str.isdigit():
            return int(date_str[:3]) + 1911
        return None
    except (ValueError, TypeError):
        return None

def GetMonth(record):
    date_field = record.get('發生日期', '')
    try:
        date_str = str(date_field)
        if len(date_str) >= 7 and date_str.isdigit():
            return int(date_str[3:5])
        return None
    except (ValueError, TypeError):
        return None

def GetTime(record):
    time_field = record.get('發生時段', '0~23')
    try:
        if '~' in str(time_field):
            start, end = str(time_field).split('~')
            return int(start), int(end)
        return 0, 23
    except (ValueError, TypeError):
        return 0, 23

def GetPlace(record):
    place_field = record.get('發生地點', '')
    try:
        if place_field.startswith('臺北市') and len(place_field) >= 6:
            district = place_field[3:6]
            if district.endswith('區'):
                return district
        return ''
    except TypeError:
        return ''

def GetYearCount(data, year):
    return sum(1 for record in data if GetYear(record) == year)

def GetMonthCount(data, month):
    return sum(1 for record in data if GetMonth(record) == month)

def GetTimeCount(data, time):
    count = 0
    for record in data:
        start, end = GetTime(record)
        if start <= time <= end:
            count += 1
    return count

def GetZoneCount(data, place):
    if not place:
        return 0
    return sum(1 for record in data if GetPlace(record) == place.strip())

def GetPlaceTimeCounts(data):
    counts = defaultdict(int)
    for record in data:
        place = GetPlace(record)
        if place:
            counts[place] += 1
    return sorted(counts.items(), key=lambda x: x[0])

def GetYearMonthCount(data, year, month):
    try:
        return sum(1 for record in data if GetYear(record) == year and GetMonth(record) == month)
    except Exception:
        return 0

def GetSafestZone(data):
    count = defaultdict(int)
    for record in data:
        place = GetPlace(record)
        if place:
            count[place] += 1
    if not count:
        return [], 0
    min_count = min(count.values())
    result = [place for place, c in count.items() if c == min_count]
    return result, min_count

def GetDangerZone(data):
    count = defaultdict(int)
    for record in data:
        place = GetPlace(record)
        if place:
            count[place] += 1
    if not count:
        return [], 0
    max_count = max(count.values())
    result = [place for place, c in count.items() if c == max_count]
    return result, max_count

@app.route('/', methods=['GET', 'POST'])
def index():
    data = GetCrimeData()
    if not data:
        return render_template('index.html', error="無法獲取資料")
    
    result = None
    if request.method == 'POST':
        choice = request.form.get('choice')
        print(f"Form data: {request.form}")  # Debugging: Log form data
        
        if choice == '1':
            try:
                qyear = request.form.get('qyear_1')
                if not qyear:
                    raise ValueError("年份不能為空")
                qyear = int(qyear)
                if 2015 <= qyear <= 2025:
                    result = f'{qyear} 年總案件數 = {GetYearCount(data, qyear)}'
                else:
                    result = '年份必須在 2015 到 2025 之間'
            except (ValueError, TypeError) as e:
                result = f'請輸入有效的年份: {str(e)}'
        
        elif choice == '2':
            try:
                qmonth = request.form.get('qmonth_2')
                if not qmonth:
                    raise ValueError("月份不能為空")
                qmonth = int(qmonth)
                if 1 <= qmonth <= 12:
                    result = f'{qmonth} 月份發生的總案件數 = {GetMonthCount(data, qmonth)}'
                else:
                    result = '月份必須在 1 到 12 之間'
            except (ValueError, TypeError) as e:
                result = f'請輸入有效的月份: {str(e)}'
        
        elif choice == '3':
            try:
                qtime = request.form.get('qtime_3')
                if not qtime:
                    raise ValueError("時間不能為空")
                qtime = int(qtime)
                if 0 <= qtime <= 23:
                    result = f'{qtime} 點發生的總案件數 = {GetTimeCount(data, qtime)}'
                else:
                    result = '時間必須在 0 到 23 之間'
            except (ValueError, TypeError) as e:
                result = f'請輸入有效的時間: {str(e)}'
        
        elif choice == '4':
            qzone = request.form.get('qzone_4', '').strip()
            if qzone:
                count = GetZoneCount(data, qzone)
                result = f'{qzone} 發生的總案件數 = {count}'
            else:
                result = '請輸入有效的區名稱（例如：中山區）'
        
        elif choice == '5':
            c = GetPlaceTimeCounts(data)
            if c:
                result = '<ul>' + ''.join([f'<li>{place}：{count} 件案件</li>' for place, count in c]) + '</ul>'
            else:
                result = '無資料可顯示'
        
        elif choice == '6':
            try:
                qyear = request.form.get('qyear_6')
                qmonth = request.form.get('qmonth_6')
                print(f"Option 6 inputs: qyear_6={qyear}, qmonth_6={qmonth}")  # Debugging
                if not qyear or not qmonth:
                    raise ValueError("年份和月份不能為空")
                qyear = int(qyear)
                qmonth = int(qmonth)
                if 2015 <= qyear <= 2025 and 1 <= qmonth <= 12:
                    count = GetYearMonthCount(data, qyear, qmonth)
                    result = f'{qyear} 年 {qmonth} 月總案件數 = {count}'
                else:
                    result = '年份必須在 2015 到 2025 之間，月份必須在 1 到 12 之間'
            except (ValueError, TypeError) as e:
                result = f'請輸入有效的年份和月份: {str(e)}'
        
        elif choice == '7':
            zones, count = GetSafestZone(data)
            if zones:
                result = f'案件最少的地區: {", ".join(zones)}，有 {count} 件'
            else:
                result = '無資料可顯示'
        
        elif choice == '8':
            zones, count = GetDangerZone(data)
            if zones:
                result = f'案件最多的地區: {", ".join(zones)}，有 {count} 件'
            else:
                result = '無資料可顯示'
    
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True,port=10000)