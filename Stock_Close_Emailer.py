import time
import yfinance as yf
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
from datetime import datetime

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Start with the browser maximized
chrome_options.add_argument("--headless")  # Enable headless mode
chrome_options.add_argument("--window-size=1920,1080")  # Set window size to mimic maximized state

# Provide the path to the ChromeDriver executable
chromedriver_path = r"C:\Users\swann\Downloads\chromedriver-win64 (4)\chromedriver-win64\chromedriver.exe"

# Function to fetch the most recent and previous closing prices for a list of tickers using yfinance
def fetch_prices(tickers):
    prices = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        try:
            # Fetch the last 2 days of data, ensuring we get the most recent available data
            hist = stock.history(period="2d", auto_adjust=False)
            if len(hist) >= 2:
                last_close_price = hist['Close'].iloc[-1]  # Most recent close
                prev_close_price = hist['Close'].iloc[-2]  # Day before the most recent close
                prices[ticker] = (round(last_close_price, 2), round(prev_close_price, 2))
            else:
                prices[ticker] = ('N/A', 'N/A')
        except Exception as e:
            print(f"An error occurred for {ticker}: {e}")
            prices[ticker] = ('Error', 'Error')
    return prices

# Function to calculate the Sortino Ratio for a stock using yfinance data
def calculate_sortino_ratio(ticker, risk_free_rate):
    stock_data = yf.Ticker(ticker)
    stock_hist = stock_data.history(period="1y")

    # Calculate the daily returns
    stock_hist['Daily Return'] = stock_hist['Close'].pct_change()

    # Calculate the Sortino Ratio
    cumulative_returns = stock_hist['Daily Return'].dropna()
    downside_returns = cumulative_returns[cumulative_returns < 0]
    downside_deviation = downside_returns.std()

    average_return = cumulative_returns.mean()

    if downside_deviation != 0:  # Avoid division by zero
        sortino_ratio = (average_return - risk_free_rate) / downside_deviation
    else:
        sortino_ratio = np.nan  # If there's no downside deviation, return NaN

    return sortino_ratio

# Fetch the 10-year Treasury yield data
treasury_data = yf.Ticker("^TNX")
treasury_hist = treasury_data.history(period="1d")
latest_yield = round(treasury_hist['Close'].iloc[-1], 2)
risk_free_rate = latest_yield / 100 / 252  # Convert annual yield to daily risk-free rate

#This is a random example portfolio
portfolios = {
    'TMT': {
        'tickers': ['AAPL', 'CRM', 'GENI', 'GOOGL', 'MGNI', 'MSFT', 'NET', 'NXPI', 'INTU'],
        'shares': {
            'AAPL': 320,
            'CRM': 219,
            'GENI': 6389,
            'GOOGL': 233,
            'MGNI': 3230,
            'MSFT': 124,
            'NET': 572,
            'NXPI': 15,
            'INTU': 3
        }
    },
    'Healthcare': {
        'tickers': ['BMY', 'DXCM', 'ENSG', 'EW', 'EXAS', 'HCA', 'ISRG', 'MCK', 'TMO', 'VRTX'],
        'shares': {
            'BMY': 52,
            'DXCM': 50,
            'ENSG': 33,
            'EW': 320,
            'EXAS': 51,
            'HCA': 142,
            'ISRG': 11,
            'MCK': 28,
            'TMO': 7,
            'VRTX': 8
        }
    },
    'Industrials': {
        'tickers': ['BXC', 'CW', 'FTV', 'LHX', 'PCAR', 'ROK', 'RTX', 'TREX', 'URI', 'WCN', 'WSC'],
        'shares': {
            'BXC': 27,
            'CW': 14,
            'FTV': 39,
            'LHX': 18,
            'PCAR': 30,
            'ROK': 132,
            'RTX': 36.4472,
            'TREX': 32,
            'URI': 2.0379,
            'WCN': 20,
            'WSC': 74
        }
    },
    'Consumer': {
        'tickers': ['CL', 'HSY', 'KO', 'LVMUY', 'MGM', 'PG', 'TGT', 'ULTA'],
        'shares': {
            'CL': 422,
            'HSY': 21,
            'KO': 62,
            'LVMUY': 21,
            'MGM': 86,
            'PG': 23,
            'TGT': 17.9761,
            'ULTA': 6,
            'MODG': 220
        }
    },
    'FIG': {
        'tickers': ['ACIW', 'APO', 'BAC', 'BRO', 'DFIN', 'IBKR', 'SSNC', 'V', 'VIRT'],
        'shares': {
            'ACIW': 78,
            'APO': 18,
            'BAC': 137,
            'BRO': 40,
            'DFIN': 57,
            'IBKR': 23,
            'SSNC': 243,
            'V': 15,
            'VIRT': 73
        }
    },
    'Energy': {
        'tickers': ['AESI', 'COP', 'ET', 'HLX', 'KMI', 'NEE', 'WMB', 'XOM', 'FCG'],
        'shares': {
            'AESI': 1322,
            'COP': 31.7071,
            'ET': 312,
            'HLX': 365,
            'KMI': 143.754,
            'NEE': 38,
            'WMB': 136.4785,
            'XOM': 315,
            'FCG': 173.9702
        }
    }
}
cash_cash_investments = 4745.46

# Index ticker to compare against
index_ticker = 'RSP'

# Fetch the prices for the index
index_prices = fetch_prices([index_ticker])

# Get the daily percentage change for the index
index_last_close, index_prev_close = index_prices[index_ticker]
if index_last_close != 'N/A' and index_prev_close != 'N/A':
    index_percent_change = ((index_last_close - index_prev_close) / index_prev_close) * 100
else:
    index_percent_change = 'N/A'

# Construct the email message
email_message = ""
portfolio_results = []
weighted_sortino_ratios = []
highest_gains_ticker = None
highest_gains = float('-inf')
highest_alpha = float('-inf')
total_portfolio_value = 0
total_portfolio_gain = 0

# Process each portfolio
for portfolio_name, portfolio_data in portfolios.items():
    tickers = portfolio_data['tickers']
    shares_owned = portfolio_data['shares']

    # Fetch the prices for the portfolio tickers
    prices = fetch_prices(tickers)

    portfolio_message = f"{portfolio_name} Results:\n"
    total_value = 0
    total_weighted_gain = 0
    total_weighted_alpha = 0
    total_weighted_sortino = 0
    total_shares = 0

    for ticker, (last_close, prev_close) in prices.items():
        if last_close != 'N/A' and prev_close != 'N/A':
            percent_change = ((last_close - prev_close) / prev_close) * 100
            if index_percent_change != 'N/A':
                alpha = percent_change - index_percent_change
            else:
                alpha = 'N/A'

            if percent_change > 0:
                gain_loss = f"{percent_change:.2f}% gain"
            else:
                gain_loss = f"({abs(percent_change):.2f}%) loss"

            if alpha != 'N/A':
                if alpha > 0:
                    alpha_str = f"{alpha:.2f}% alpha"
                else:
                    alpha_str = f"({abs(alpha):.2f}%) alpha"
            else:
                alpha_str = "N/A alpha"

            portfolio_message += f"• {ticker}: ${last_close}; {gain_loss}; {alpha_str}\n"

            # Calculate weighted gain, alpha, and Sortino Ratio
            shares = shares_owned.get(ticker, 0)
            total_value += last_close * shares
            total_weighted_gain += (percent_change * last_close * shares)
            total_weighted_alpha += (alpha * last_close * shares) if alpha != 'N/A' else 0
            total_weighted_sortino += calculate_sortino_ratio(ticker, risk_free_rate) * shares
            total_shares += shares

            # Track the highest gains and alpha
            if percent_change > highest_gains:
                highest_gains = percent_change
                highest_gains_ticker = ticker
                highest_gains_alpha = alpha
        else:
            portfolio_message += f"• {ticker}: {last_close}\n"

    # Calculate the weighted average gain, alpha, and Sortino Ratio
    if total_value > 0:
        weighted_average_gain = total_weighted_gain / total_value
        weighted_average_alpha = total_weighted_alpha / total_value
        weighted_average_sortino = total_weighted_sortino / total_shares if total_shares > 0 else np.nan

        if weighted_average_gain > 0:
            weighted_gain_str = f"{weighted_average_gain:.2f}%"
        else:
            weighted_gain_str = f"({abs(weighted_average_gain):.2f}%)"

        if weighted_average_alpha > 0:
            weighted_alpha_str = f"{weighted_average_alpha:.2f}%"
        else:
            weighted_alpha_str = f"({abs(weighted_average_alpha):.2f}%)"

        portfolio_message += f"Weighted average gain for the {portfolio_name} portfolio: {weighted_gain_str}\n"
        portfolio_message += f"Weighted average alpha for the {portfolio_name} portfolio: {weighted_alpha_str}\n\n"

    else:
        weighted_average_sortino = np.nan  # Handle portfolios with no value
        portfolio_message += f"Weighted average gain for the {portfolio_name} portfolio: N/A\n"
        portfolio_message += f"Weighted average alpha for the {portfolio_name} portfolio: N/A\n\n"

    portfolio_results.append((portfolio_name, weighted_average_gain, weighted_average_alpha, total_value, total_weighted_gain, portfolio_message))
    weighted_sortino_ratios.append((portfolio_name, weighted_average_sortino))
    total_portfolio_value += total_value
    total_portfolio_gain += total_weighted_gain

# Identify the portfolio with the largest daily gains
winning_portfolio = max(portfolio_results, key=lambda x: x[1])

# Calculate overall portfolio performance
if total_portfolio_value > 0:
    total_weighted_average_gain = total_portfolio_gain / total_portfolio_value
    total_alpha = total_weighted_average_gain - index_percent_change
    if total_weighted_average_gain > 0:
        total_gain_str = f"{total_weighted_average_gain:.2f}%"
    else:
        total_gain_str = f"({abs(total_weighted_average_gain):.2f}%)"
    if total_alpha > 0:
        total_alpha_str = f"{total_alpha:.2f}%"
    else:
        total_alpha_str = f"({abs(total_alpha):.2f}%)"

    # Calculate the total cash generated
    total_cash_generated = round((total_weighted_average_gain / 100) * total_portfolio_value)
else:
    total_gain_str = "N/A"
    total_alpha_str = "N/A"
    total_cash_generated = 0

# Format total cash with appropriate commas
if total_cash_generated < 0:
    total_cash_generated_str = f"(${abs(total_cash_generated):,})"
else:
    total_cash_generated_str = f"${total_cash_generated:,}"

# Correct the highest gains and alpha output
highest_gains_ticker_info = [
    (line.split(':')[0].replace('- $', '').strip(), float(line.split(';')[1].split('%')[0].replace('(', '-').replace(')', '')))
    for line in winning_portfolio[5].split('\n')[1:-1]
    if ';' in line
]

highest_gains_ticker = max(highest_gains_ticker_info, key=lambda x: x[1])[0]

# Construct the summary message
summary_message = (f"• The {winning_portfolio[0]} portfolio had the largest daily gains with "
                   f"{winning_portfolio[1]:.2f}% gains and {winning_portfolio[2]:.2f}% alpha.\n"
                   f"{highest_gains_ticker} helped drive the {winning_portfolio[0]} portfolio with "
                   f"{highest_gains:.2f}% gains and {highest_gains_alpha:.2f}% alpha.\n"
                   f"• Today BIG had {total_gain_str} gains and {total_alpha_str} alpha, generating ~{total_cash_generated_str} in unrealized gains.\n\n")

# Combine the summary message and the detailed portfolio results
email_message = summary_message + ''.join([result[5] for result in portfolio_results])

# Add RSP to the portfolio results for the bar chart
portfolio_names = [result[0] for result in portfolio_results] + ["Benchmark"]
portfolio_gains = [result[1] for result in portfolio_results] + [index_percent_change]

plt.figure(figsize=(10, 6))

# Format the y-axis labels
def y_axis_formatter(x, pos):
    if x < 0:
        return f"({abs(x):.1f}%)"
    else:
        return f"{x:.1f}%"

# Determine the bar colors based on comparison with RSP
colors = []
for gain in portfolio_gains[:-1]:  # Exclude RSP for dynamic color determination
    if gain > index_percent_change:
        colors.append((218/255, 242/255, 208/255, 1))  # Green RGB for greater than RSP
    else:
        colors.append((255/255, 125/255, 125/255, 1))  # Red RGB for less than RSP

colors.append((255/255, 235/255, 123/255, 1))  # RGB for RSP (Gold)

bars = plt.bar(portfolio_names, portfolio_gains, color=colors)

# Calculate the offset for negative percentages
tick_interval = plt.gca().yaxis.get_ticklocs()[1] - plt.gca().yaxis.get_ticklocs()[0]
negative_offset = tick_interval * 0.25

# Add percentage labels on top of each bar
for bar, gain in zip(bars, portfolio_gains):
    height = bar.get_height() if gain >= 0 else negative_offset
    gain_label = f"{gain:.2f}%" if gain >= 0 else f"({abs(gain):.2f}%)"
    plt.text(bar.get_x() + bar.get_width() / 2.0, height, gain_label, ha='center', va='bottom' if gain >= 0 else 'top')

plt.xlabel('') #I think this looks better
plt.ylabel('') #I think this looks better
current_date = datetime.now().strftime("%m/%d/%Y").lstrip('0').replace('/0', '/')
plt.title(f'BIG Daily Gains Scorecard - {current_date}', fontweight='bold')
plt.xticks(rotation=0)

# Apply the custom y-axis formatter
plt.gca().yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))

plt.tight_layout()

# Save the first chart (daily gains)
daily_gains_chart_path = r"C:\Users\swann\Downloads\BIG_Portfolio_Daily_Gains.png"
plt.savefig(daily_gains_chart_path)
plt.close()

# Generate the second bar chart for Sortino Ratios
portfolio_names = [result[0] for result in weighted_sortino_ratios]
sortino_ratios = [result[1] for result in weighted_sortino_ratios]

plt.figure(figsize=(10, 6))
bars = plt.bar(portfolio_names, sortino_ratios, color=(36/255, 87/255, 133/255, 1))  # Same color for all bars

# Add Sortino Ratio labels on top of each bar
for bar, sortino in zip(bars, sortino_ratios):
    plt.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height(), f"{sortino:.2f}", ha='center', va='bottom')

plt.xlabel('') #I think this looks better
plt.ylabel('') #I think this looks better
plt.title(f'BIG Portfolio Daily Sortino Ratios - {current_date}', fontweight='bold')
plt.xticks(rotation=0)
plt.tight_layout()

# Save the second chart (Sortino Ratios)
sortino_ratios_chart_path = r"C:\Users\swann\Downloads\BIG_Portfolio_Sortino_Ratios.png"
plt.savefig(sortino_ratios_chart_path)
plt.close()

# Generate the pie charts for portfolio holdings
# Define the specific RGB colors
colors = [
    (36/255, 87/255, 133/255),   # Base Color (Blue)
    (82/255, 128/255, 168/255),  # Light Blue
    (21/255, 68/255, 104/255),   # Dark Blue
    (70/255, 106/255, 135/255),  # Steel Blue
    (108/255, 149/255, 185/255), # Sky Blue
    (45/255, 100/255, 142/255),  # Slate Blue
    (200/255, 200/255, 200/255), # Light Gray
    (150/255, 150/255, 150/255), # Medium Gray
    (100/255, 100/255, 100/255), # Dark Gray
    (55/255, 55/255, 55/255),    # Charcoal
    (130/255, 138/255, 143/255)  # Cool Gray
]

# Aggregate the total value of each portfolio
portfolio_totals = {}
for sector, data in portfolios.items():
    portfolio_totals[sector] = sum(data['shares'].values())

# Customization options
label_fontsize = 16  # Font size for tickers
label_color = 'black'  # Color for tickers
autopct_fontsize = 16  # Font size for percentages
autopct_color = 'white'  # Color for percentages
border_color = 'black'  # Color of the border
border_thickness = 0.5  # Thickness of the border

# Create the figure
fig = plt.figure(figsize=(20, 20))

# Add the main title
fig.suptitle(f'BIG Portfolio Holdings - {current_date}', fontsize=30, fontweight='bold')

# Main pie chart settings
main_pie_size = [0.3, 0.28, 0.4, 0.4]  # [x, y, width, height] in normalized (0 to 1) coordinates

# Function to customize the autopct label color and font size
def make_autopct(color, fontsize):
    def my_autopct(pct):
        return f'{pct:.1f}%' if pct > 0 else ''
    return {'color': color, 'fontsize': fontsize}

# Create the main pie chart (center)
ax_main = fig.add_axes(main_pie_size)
wedges, texts, autotexts = ax_main.pie(portfolio_totals.values(), labels=portfolio_totals.keys(), autopct='%1.1f%%', startangle=140,
                                       wedgeprops=dict(edgecolor=border_color, linewidth=border_thickness), colors=colors)
ax_main.set_title('Portfolio Distribution', fontsize=20, fontweight='bold')

# Customize font size and color for main pie chart
for text in texts:
    text.set_fontsize(label_fontsize)
    text.set_color(label_color)
for autotext in autotexts:
    autotext.set_fontsize(autopct_fontsize)
    autotext.set_color(autopct_color)

# Individual pie charts settings (customize these positions)
small_pie_positions = {
    'Healthcare': [0.01, 0.65, 0.3, 0.3],  # Top-right
    'FIG': [0.01, 0.325, 0.3, 0.3],  # Middle-left
    'TMT': [0.01, 0.0, 0.3, 0.3],  # Top-left
    'Energy': [0.69, 0.65, 0.3, 0.3],  # Middle-right
    'Industrials': [0.69, 0.325, 0.3, 0.3],  # Bottom-left
    'Consumer': [0.69, 0.0, 0.3, 0.3],  # Bottom-right
}

# Add the individual pie charts
for sector, pos in small_pie_positions.items():
    tickers = list(portfolios[sector]['shares'].keys())
    shares = [portfolios[sector]['shares'][ticker] for ticker in tickers]

    ax = fig.add_axes(pos)
    wedges, texts, autotexts = ax.pie(shares, labels=tickers, autopct='%1.1f%%', startangle=140,
                                      wedgeprops=dict(edgecolor=border_color, linewidth=border_thickness), colors=colors)
    ax.set_title(f'{sector} Portfolio', fontsize=18, fontweight='bold')

    # Customize font size and color for individual pie charts
    for text in texts:
        text.set_fontsize(label_fontsize)
        text.set_color(label_color)
    for autotext in autotexts:
        autotext.set_fontsize(autopct_fontsize)
        autotext.set_color(autopct_color)

# Save the pie chart figure
pie_chart_path = r'C:\Users\swann\Downloads\BIG_Holdings_All_Pie.png'
plt.savefig(pie_chart_path)
plt.close()

# Set the email content
recipient_emails = [
# Fill in emails here,
]
email_subject = "BIG Daily Stock Performance"

# Create a new instance of the Chrome driver
driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)

# Open the specified Gmail compose link
driver.get("https://mail.google.com/mail/u/0/#inbox?compose=new")

try:
    # Wait for the 'email or phone' field to be present and then click it
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
    )
    email_field.click()

    # Type the email address into the field
    email_field.send_keys("emailtestbot1234@gmail.com")

    # Wait for the 'Next' button to be clickable and then click it
    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "identifierNext"))
    )
    next_button.click()

    # Wait for the 'Enter your password' field to be present
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "Passwd"))
    )
    # Directly send the password to the focused field
    password_field.send_keys("ashtashtASHTASHT9!")

    # Wait for the 'Next' button after password to be clickable and then click it
    password_next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "passwordNext"))
    )
    password_next_button.click()

    # Click the 'Compose' button
    compose_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.T-I.T-I-KE.L3"))
    )
    compose_button.click()

    # Loop to enter each recipient email address
    for recipient_email in recipient_emails:
        # Wait for the 'To' field to be clickable and then enter the recipient email
        to_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[aria-label='To recipients']"))
        )
        to_field.click()
        to_field.send_keys(recipient_email)

        # Simulate hitting the Enter key
        to_field.send_keys(Keys.RETURN)

    # Simulate pressing the Tab key after entering all recipient email addresses
    to_field.send_keys(Keys.TAB)

    # Wait for the 'Subject' field to be clickable and then enter the subject
    subject_field = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "subjectbox"))
    )
    subject_field.click()
    subject_field.send_keys(email_subject)

    # Simulate pressing the Tab key after entering the subject
    subject_field.send_keys(Keys.TAB)

    # Wait for the message body to be clickable and then enter the message
    message_body = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div[aria-label='Message Body']"))
    )
    message_body.click()
    message_body.send_keys(email_message)

    # Attach the first chart (daily gains)
    attach_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div[command='Files']"))
    )
    attach_button.click()
    time.sleep(2)

    file_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    file_input.send_keys(daily_gains_chart_path)
    time.sleep(2)

    # Attach the second chart (Sortino Ratios)
    attach_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div[command='Files']"))
    )
    attach_button.click()
    time.sleep(2)

    file_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    file_input.send_keys(sortino_ratios_chart_path)
    time.sleep(2)

    # Attach the third chart (Pie Chart)
    attach_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div[command='Files']"))
    )
    attach_button.click()
    time.sleep(2)

    file_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    file_input.send_keys(pie_chart_path)
    time.sleep(2)

    # Send the email by simulating pressing Ctrl + Enter
    message_body.send_keys(Keys.CONTROL, Keys.RETURN)
    time.sleep(2)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser tab
    driver.close()
    time.sleep(5)

    # Quit the driver (optional)
    # driver.quit()  # Uncomment this line to quit the browser entirely
