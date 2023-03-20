import pandas as pd
import datetime


def convert_to_date(s):
    try:
        out_val = datetime.datetime.strptime(s, '%d/%m/%Y')
    except:
        try:
            out_val = datetime.datetime.strptime(s, '%d/%m/%y')
        except:
          try:
            out_val = datetime.datetime.strptime(s, '%d-%m-%Y')
          except:
            try:
              out_val = datetime.datetime.strptime(s, '%d-%m-%y')
            except:
              print(s)
    return out_val


def compare_candle(date_val, today_open):
  global df
  global output
  date_df = df.loc[df['Date'] == date_val]
  # print(date_val)
  # print(df['Date'])
  
  try:
    today_close = df.loc[(df['Date'] == (date_val)) & (df['Time'] == '15:14:59')]['Close'].iloc[0]  
  except:
    pass
  for i in range(50):
    try:
      prev_day_close = df.loc[(df['Date'] == (date_val - datetime.timedelta(days = i + 1))) & (df['Time'] == '15:14:59')]['Close'].iloc[0]
      break
    except:
      prev_day_close = today_close
  pattern = '%H:%M:%S'
  # df['Time'] = df['Time'].apply(datetime.datetime.strptime, args = (pattern, ))
  today_high = max(df.loc[(df['Date'] == (date_val)) & (df['Time'] >= '09:15:59') & (df['Time'] <= '15:14:59')]['High'])
  today_low = min(df.loc[(df['Date'] == (date_val)) & (df['Time'] >= '09:15:59') & (df['Time'] <= '15:14:59')]['Low']) 

  if today_open < prev_day_close:
    gap_down = True
  else:
    gap_down = False
  # print(gap_down)
  
  date_df['Time'] = date_df['Time'].apply(datetime.datetime.strptime, args = (pattern, ))
  start = datetime.datetime.strptime('09:15:59' , pattern)
  # print(start)
  end = start + datetime.timedelta(minutes=30)
  candle_start_df = date_df.loc[(date_df['Time'] >= start) & (date_df['Time'] < end)]
  start = end
  if gap_down:
    low = min(candle_start_df['Low'])
    high = None
    gap = 'Down'
  else:
    high = max(candle_start_df['High'])
    low = None
    gap = 'Up'
  gap_points = today_open - prev_day_close
  if abs(gap_points / today_open) * 100 > 1:
    for candle in range(12):
      candle_close = date_df.loc[date_df['Time'] == start]['Close'].iloc[0]
      out = None
      if gap_down:
        if candle_close < low:
          out = 'No'
          
      else:
        if candle_close > high:
          out = 'Yes'
          
      
      output.append([str(date_val)[:-9], str(start)[11:], prev_day_close, today_open, today_high, today_close ,gap, today_open - prev_day_close ,candle_close, low, high, out])

      start = start + datetime.timedelta(minutes=30)

df = pd.read_csv("Banknifty_2019.csv")
df['Date'] = df.Date.apply(convert_to_date)
open_close_df = df.loc[df.Time.isin(['09:15:59', '15:14:59'])].sort_values(by = ['Date', 'Time'])

group = (open_close_df.groupby(['Date']).agg('count')['Time'].reset_index())
both_values = group.loc[group['Time'] == 2][['Date']]
open_close_df = open_close_df.loc[(open_close_df.Date.isin(both_values.Date))]
# print(open_close_df)
# new_df = open_close_df.loc[(((abs((open_close_df.Open - open_close_df.Close.shift(1)) / open_close_df.Open) * 100)) > 1)]
new_df = open_close_df.loc[(open_close_df.Time == '09:15:59')]
# print(new_df)
# print((((abs((open_close_df.Open - open_close_df.Close.shift(2)) / open_close_df.Open) * 100)) > 1) & (open_close_df.Time == '09:15:59'))

# print(new_df['Date'])

output = list()


new_df.apply(lambda x :compare_candle(x['Date'] , x['Open']) , axis = 1)
out_df = pd.DataFrame(output, columns=['Date', 'Candle Start Time', 'Previous close', 'TOPEN', 'THigh', 'Tlow',  'Gap', 'Gap Points', 'Candle Close', 'Low', 'High', 'Output'])
out_df.to_csv('30min_gap_2019.csv', index=False)
