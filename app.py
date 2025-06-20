from flask import Flask, render_template, request, redirect, url_for, session
import requests
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 設置 session 需要的密鑰

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
    if request.method == 'POST':
        data = GetCrimeData()
        if not data:
            session['error'] = "無法獲取資料，請稍後再試"
            return redirect(url_for('result'))
        
        choice = request.form.get('choice')
        result = None
        query_info = None
        
        try:
            if choice == '1':
                qyear = request.form.get('qyear_1')
                if not qyear:
                    raise ValueError("年份不能為空")
                qyear = int(qyear)
                if 2015 <= qyear <= 2025:
                    count = GetYearCount(data, qyear)
                    result = f'<div class="text-center"><div class="text-4xl font-bold text-blue-600 mb-2">{count:,}</div><div class="text-lg">件自行車竊盜案件</div></div>'
                    query_info = f'查詢 {qyear} 年的案件總數'
                else:
                    raise ValueError('年份必須在 2015 到 2025 之間')
            
            elif choice == '2':
                qmonth = request.form.get('qmonth_2')
                if not qmonth:
                    raise ValueError("月份不能為空")
                qmonth = int(qmonth)
                if 1 <= qmonth <= 12:
                    count = GetMonthCount(data, qmonth)
                    result = f'<div class="text-center"><div class="text-4xl font-bold text-blue-600 mb-2">{count:,}</div><div class="text-lg">件自行車竊盜案件</div></div>'
                    query_info = f'查詢 {qmonth} 月份的案件總數'
                else:
                    raise ValueError('月份必須在 1 到 12 之間')
            
            elif choice == '3':
                qtime = request.form.get('qtime_3')
                if not qtime:
                    raise ValueError("時間不能為空")
                qtime = int(qtime)
                if 0 <= qtime <= 23:
                    count = GetTimeCount(data, qtime)
                    result = f'<div class="text-center"><div class="text-4xl font-bold text-blue-600 mb-2">{count:,}</div><div class="text-lg">件自行車竊盜案件</div></div>'
                    query_info = f'查詢 {qtime} 點時段的案件總數'
                else:
                    raise ValueError('時間必須在 0 到 23 之間')
            
            elif choice == '4':
                qzone = request.form.get('qzone_4', '').strip()
                if qzone:
                    count = GetZoneCount(data, qzone)
                    result = f'<div class="text-center"><div class="text-4xl font-bold text-blue-600 mb-2">{count:,}</div><div class="text-lg">件自行車竊盜案件</div></div>'
                    query_info = f'查詢 {qzone} 的案件總數'
                else:
                    raise ValueError('請選擇一個行政區域')
            
            elif choice == '5':
                c = GetPlaceTimeCounts(data)
                if c:
                    result_items = []
                    for place, count in c:
                        result_items.append(f'<div class="flex justify-between items-center py-2 border-b border-gray-200"><span class="font-medium">{place}</span><span class="text-blue-600 font-bold">{count:,} 件</span></div>')
                    result = '<div class="space-y-1">' + ''.join(result_items) + '</div>'
                    query_info = '各行政區域案件數統計分析'
                else:
                    raise ValueError('無資料可顯示')
            
            elif choice == '6':
                qyear = request.form.get('qyear_6')
                qmonth = request.form.get('qmonth_6')
                if not qyear or not qmonth:
                    raise ValueError("年份和月份不能為空")
                qyear = int(qyear)
                qmonth = int(qmonth)
                if 2015 <= qyear <= 2025 and 1 <= qmonth <= 12:
                    count = GetYearMonthCount(data, qyear, qmonth)
                    result = f'<div class="text-center"><div class="text-4xl font-bold text-blue-600 mb-2">{count:,}</div><div class="text-lg">件自行車竊盜案件</div></div>'
                    query_info = f'查詢 {qyear} 年 {qmonth} 月的案件總數'
                else:
                    raise ValueError('年份必須在 2015 到 2025 之間，月份必須在 1 到 12 之間')
            
            elif choice == '7':
                zones, count = GetSafestZone(data)
                if zones:
                    zone_list = ', '.join(zones)
                    result = f'<div class="text-center"><div class="text-2xl font-bold text-green-600 mb-4">{zone_list}</div><div class="text-lg mb-2">案件數最少的區域</div><div class="text-3xl font-bold text-blue-600">{count:,} 件</div></div>'
                    query_info = '查詢案件數最少的安全區域'
                else:
                    raise ValueError('無資料可顯示')
            
            elif choice == '8':
                zones, count = GetDangerZone(data)
                if zones:
                    zone_list = ', '.join(zones)
                    result = f'<div class="text-center"><div class="text-2xl font-bold text-red-600 mb-4">{zone_list}</div><div class="text-lg mb-2">案件數最多的區域</div><div class="text-3xl font-bold text-blue-600">{count:,} 件</div></div>'
                    query_info = '查詢案件數最多的高風險區域'
                else:
                    raise ValueError('無資料可顯示')
            
            else:
                raise ValueError('無效的查詢選項')
            
            # 將結果存入 session 並跳轉到結果頁面
            session['result'] = result
            session['query_info'] = query_info
            session['timestamp'] = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
            return redirect(url_for('result'))
            
        except (ValueError, TypeError) as e:
            session['error'] = str(e)
            return redirect(url_for('result'))
    
    return render_template('index.html')

@app.route('/result')
def result():
    result = session.pop('result', None)
    error = session.pop('error', None)
    query_info = session.pop('query_info', None)
    timestamp = session.pop('timestamp', datetime.now().strftime('%Y年%m月%d日 %H:%M:%S'))
    
    return render_template('result.html', 
                         result=result, 
                         error=error, 
                         query_info=query_info,
                         timestamp=timestamp)

if __name__ == '__main__':
    app.run(debug=True,port=10000)
