import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import skew, kurtosis, norm, jarque_bera,linregress
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np
from scipy.stats.mstats import gmean
from prompts import format_stats_for_prompt, generate_ai_response,generate_anomaly_analytics_prompt,generate_ai_response_anomaly
from sklearn.ensemble import IsolationForest
from collections import defaultdict
import calendar
from datetime import datetime

# Function to fetch NEAR Blocks API data
def fetch_near_blocks_stats():
    url = "https://api.nearblocks.io/v1/stats"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        st.error("Failed to fetch NEAR Blocks API data.")
        return {}

# Function to fetch NEAR-USD data
def get_near_data(start_date, end_date):
    near = yf.Ticker("NEAR-USD")
    return near.history(start=start_date, end=end_date)

# Function to display basic data and plots
def display_basic_data(df):
    st.subheader("Basic NEAR-USD analysis")
    st.write(df.describe())  # Display basic statistics
    st.line_chart(df['Close'])  # Line chart for closing prices

# Function for statistical analysis
def statistical_analysis(df):
    st.subheader("Statistical Analysis")
    returns = df['Close'].pct_change().dropna()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background-color:#f0f2f6;padding:10px;border-radius:10px;">
            <h4 style="color:#333;">Mean:</h4>
            <p style="color:red;">{returns.mean()}</p>
            <h4 style="color:#333;">Median:</h4>
            <p style="color:red;">{returns.median()}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background-color:#f0f2f6;padding:10px;border-radius:10px;">
            <h4 style="color:#333;">Min:</h4>
            <p style="color:red;">{returns.min()}</p>
            <h4 style="color:#333;">Max:</h4>
            <p style="color:red;">{returns.max()}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background-color:#e8eaf6;padding:10px;border-radius:10px;">
        <h4 style="color:#333;">Standard Deviation:</h4>
        <p style="color:red;">{returns.std()}</p>
    </div>
    """, unsafe_allow_html=True)
    # Histogram with normal distribution fit
    plt.figure(figsize=(10, 6))
    sns.histplot(returns, kde=True, stat="density", linewidth=0)
    mu, std = norm.fit(returns)
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    plt.plot(x, p, 'k', linewidth=2)
    title = f"Fit results: mu = {mu:.2f}, std = {std:.2f}"
    plt.title("Normal Density Function")
    st.pyplot(plt)
    plt.close()

# Function for distribution fitting
def distribution_fitting(returns):
    sns.distplot(returns, fit=norm, kde=False)
    plt.title("Normal Distribution Fit")
    st.pyplot(plt)
    plt.close()

# Function for stock price predictions
def stock_price_predictions(df):
    st.subheader("Stock Price Predictions & Accuracy Score")
    # Simplified prediction model using closing prices
    X = df[['Open']]
    y = df['Close']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    st.markdown(f"""
    <div style="background-color:#e8eaf6;padding:10px;border-radius:10px;">
        <h4 style="color:#333;">Model Accuracy Score:</h4>
        <p style="color:red;">{score:.2f}</p>
    </div>
    """, unsafe_allow_html=True)
    return score

# Function for Value at Risk
def value_at_risk(df):
    st.subheader("Value at Risk (VaR)")
    returns = df['Close'].pct_change().dropna()
    st.bar_chart(returns)
    st.markdown(f"""
    <div style="background-color:#f0f2f6;padding:10px;border-radius:10px;margin-bottom:10px;">
        <h4 style="color:#333;">Standard deviation:</h4>
        <p style="color:red;">{returns.std():.2f}</p>
    </div>
    <div style="background-color:#f0f2f6;padding:10px;border-radius:10px;">
        <h4 style="color:#333;">Inter-Quantile range:</h4>
        <p style="color:red;">{returns.quantile(0.05):.2f}</p>
    </div>
    """, unsafe_allow_html=True)

# Function for time series forecast
def time_series_forecast(df):
    st.subheader("Time Series Forecast")
    logged_close = np.log(df['Close'])
    st.line_chart(logged_close)

# Function for Covariance & Correlations analysis
def covariance_correlations(df):
    st.subheader("Volatility Analysis")
    returns = np.log(df['Close'] / df['Close'].shift(1)).dropna()
    variance = returns.var()
    std_dev = np.sqrt(variance)
    st.markdown(f"""
    <div style="background-color:#f0f2f6;padding:10px;border-radius:10px;margin-bottom:10px;">
        <h4 style="color:#333;">Variance :</h4>
        <p style="color:red;">{variance}</p>
    </div>
    <div style="background-color:#f0f2f6;padding:10px;border-radius:10px;">
        <h4 style="color:#333;">Standard deviation:</h4>
        <p style="color:red;">{std_dev}</p>
    </div>
    """, unsafe_allow_html=True)

# Function for Linear Regression analysis
def linear_regression(df):
    st.subheader("Linear Regression (Graphical representation)")
    df = df.dropna()
    X = df[['Open']]
    y = df['Close']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    plt.scatter(X_train, y_train, color='blue')
    plt.plot(X_train, model.predict(X_train), color='red')
    plt.title("Linear Regression")
    plt.xlabel("Open Price")
    plt.ylabel("Close Price")
    st.pyplot(plt)
    plt.close()

# Function for Stock Statistics
def stock_statistics(df):
    st.subheader("Stock Statistics")
    returns = df['Close'].pct_change().dropna()
    mean = returns.mean()
    median = returns.median()
    skewness = skew(returns)
    kurt = kurtosis(returns)
    jb_stat, pvalue = jarque_bera(returns)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div style="background-color:#f0f2f6;padding:10px;border-radius:10px;">
            <h4 style="color:#333;">Mean:</h4>
            <p style="color:red;">{mean:.4f}</p>
            <h4 style="color:#333;">Median:</h4>
            <p style="color:red;">{median:.4f}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background-color:#f0f2f6;padding:10px;border-radius:10px;">
            <h4 style="color:#333;">Skew:</h4>
            <p style="color:red;">{skewness:.4f}</p>
            <h4 style="color:#333;">Kurtosis:</h4>
            <p style="color:red;">{kurt:.4f}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background-color:#e8eaf6;padding:10px;border-radius:10px;">
        <h4 style="color:#333;">Jarque-Bera Test:</h4>
        <p style="color:red;">Statistic: {jb_stat:.2f}, P-value: {pvalue:.2e}</p>
    </div>
    """, unsafe_allow_html=True)

    if pvalue > 0.05:
        st.success("The returns are likely normal.")
    else:
        st.error("The returns are likely not normal.")

# Beta calculation (using NEAR-USD as market proxy)
def beta_calculation(df):
    st.subheader("Market Sensitivity Analysis: NEAR-USD vs. BTC-USD")
    # Download market data
    market_df = yf.download('BTC-USD', df.index.min(), df.index.max())['Adj Close']
    # Convert to timezone-naive datetime index if it's timezone-aware
    if market_df.index.tz is not None:
        market_df.index = market_df.index.tz_localize(None)

    # Calculate returns and ensure timezone-naive index for NEAR data as well
    market_ret = market_df.pct_change().dropna()
    near_ret = df['Close'].pct_change().dropna()
    if near_ret.index.tz is not None:
        near_ret.index = near_ret.index.tz_localize(None)

    # Align the data by date
    aligned_data = pd.merge(market_ret.rename('Market'), near_ret.rename('NEAR'), left_index=True, right_index=True, how='inner')

    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = linregress(aligned_data['Market'], aligned_data['NEAR'])

    st.markdown(f"""
    <div style="background-color:#f0f2f6;padding:10px;border-radius:10px;margin-bottom:10px;">
        <h4 style="color:#333;">Beta (slope):</h4>
        <p style="color:red;">{slope:.2f}</p>
    </div>
    <div style="background-color:#f0f2f6;padding:10px;border-radius:10px;">
        <h4 style="color:#333;">Alpha (intercept):</h4>
        <p style="color:red;">{intercept:.4f}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Plotting the scatter plot of returns
    plt.subplots()
    plt.scatter(aligned_data['Market'], aligned_data['NEAR'], alpha=0.5)
    plt.plot(aligned_data['Market'], intercept + slope * aligned_data['Market'], 'r', label='fitted line')
    plt.xlabel('BTC-USD Returns')
    plt.ylabel('NEAR-USD Returns')
    plt.title('Market Sensitivity Analysis: NEAR-USD vs. BTC-USD')
    plt.legend()
    st.pyplot(plt)
    plt.close()

def summarize_findings(df):
    # Statistical Analysis Metrics
    mean_return = df['Close'].pct_change().mean()
    min_return = df['Close'].pct_change().min()
    max_return = df['Close'].pct_change().max()
    median_return = df['Close'].pct_change().median()
    std_deviation = df['Close'].pct_change().std()
    # Value at Risk Metric
    inter_quantile_range = df['Close'].pct_change().quantile(0.05)
    # Covariance & Correlations Analysis Metric
    returns = np.log(df['Close'] / df['Close'].shift(1)).dropna()
    variance = returns.var()
    # Stock Statistics Metrics
    skewness = skew(returns)
    kurtosis_value = kurtosis(returns)
    jb_stat, pvalue = jarque_bera(returns)
    normality = "likely normal" if pvalue > 0.05 else "likely not normal"
    # Get the model accuracy score from the stock_price_predictions function
    model_accuracy_score = stock_price_predictions(df)
    # Stock Price Predictions Metric
    model_accuracy = model_accuracy_score  # Now using the actual score from your analysis

    # Fetch NEAR Blocks API data
    near_blocks_data = fetch_near_blocks_stats()
    high_24h = near_blocks_data.get("high_24h", "N/A")
    high_all = near_blocks_data.get("high_all", "N/A")
    low_24h = near_blocks_data.get("low_24h", "N/A")
    low_all = near_blocks_data.get("low_all", "N/A")
    change_24 = near_blocks_data.get("change_24", "N/A")

    # Combine all findings into a summary
    summary = f"""
    - Mean Return: {mean_return:.4f}
    - Min Return: {min_return:.4f}
    - Max Return: {max_return:.4f}
    - Median Return: {median_return:.4f}
    - Standard Deviation: {std_deviation:.4f}
    - Inter-Quantile Range: {inter_quantile_range:.4f}
    - Variance: {variance:.4f}
    - Skewness: {skewness:.4f}
    - Kurtosis: {kurtosis_value:.4f}
    - Jarque-Bera Test: {jb_stat:.2f}, P-value: {pvalue:.2e} ({normality})
    - Model Accuracy Score: {model_accuracy}
    - 24h High: {high_24h}
    - All-Time High: {high_all}
    - 24h Low: {low_24h}
    - All-Time Low: {low_all}
    - 24h Change: {change_24}
    - Model Accuracy Score: {model_accuracy:.2f}
    """
    return summary

def generate_prediction(summary, api_key):
    prompt = format_stats_for_prompt(summary)
    prediction = generate_ai_response(prompt, api_key)
    return prediction

def summarize_anomalies(anomaly_dates):
    summary = {}
    summary = defaultdict(int)
    for date in anomaly_dates:
        month_year = date.strftime("%B %Y")
        if month_year in summary:
            summary[month_year] += 1
        else:
            summary[month_year] = 1
    return summary

def generate_input_prompt(anomaly_summary):
    prompt = "Here is a list of detected anomalies in particular months:\n\n"
    for month_year, count in anomaly_summary.items():
        prompt += f"{month_year}: {count} anomalies\n\n"
    # Add more to the prompt as needed
    return prompt

def anomaly_detection(df):
    st.subheader("Anomaly Detection in NEAR-USD Trading Patterns")

    data = df[['Close']].copy()
    isolation_forest = IsolationForest(n_estimators=100, contamination='auto', random_state=42)
    anomalies = isolation_forest.fit_predict(data)
    data['Anomaly'] = anomalies
    anomaly_data = data[data['Anomaly'] == -1]

    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'], color='blue', label='Normal')
    plt.scatter(anomaly_data.index, anomaly_data['Close'], color='red', label='Anomaly')
    plt.title("Anomaly Detection in NEAR-USD Trading Patterns")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.legend()
    st.pyplot(plt)
    plt.close()

    if not anomaly_data.empty:
        anomaly_dates = sorted(anomaly_data.index.to_list())  # Ensure these are datetime objects
        anomaly_summary = summarize_anomalies(anomaly_dates)
        input_prompt = generate_input_prompt(anomaly_summary)
        
        # Display the input prompt
        st.markdown(f"<div style='padding: 10px; border-radius: 10px; background-color: #e1f5fe; margin-bottom: 10px;'>👤 <strong>Input prompt:</strong><br>{input_prompt}</div>", unsafe_allow_html=True)

        analytics_prompt = generate_anomaly_analytics_prompt(anomaly_dates)
        analytics_response = generate_ai_response_anomaly(analytics_prompt, st.secrets["API_KEY"])

        # Splitting the response into individual lines and adding line breaks for Streamlit
        response_lines = analytics_response.split("\n")
        formatted_response = "<br>".join(response_lines)

        st.markdown(f"""
        <div style='padding: 10px; border-radius: 10px; background-color: #f0f4c3; margin-bottom: 10px;'>
            🤖 <strong>Anomaly Analysis:</strong><br>{formatted_response}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background-color:#f0f2f6;padding:10px;border-radius:10px;margin-bottom:10px;">
            <h4 style="color:#333;">Detected Anomalies:</h4>
            <p style="color:red;">No anomalies detected with the current settings.</p>
        </div>
        """, unsafe_allow_html=True)

# Main app function
def app():
    st.title('🕵🏻 Real Time Insights and Anomaly detection')
    start_date = st.date_input("Start Date", value=pd.to_datetime('2023-01-01'))
    end_date = st.date_input("End Date", value=pd.to_datetime('today'))
    df = get_near_data(start_date, end_date)

    if not df.empty:
        display_basic_data(df)
        statistical_analysis(df)
        distribution_fitting(df)
        value_at_risk(df)
        time_series_forecast(df)
        covariance_correlations(df)
        stock_statistics(df)
        beta_calculation(df)
        linear_regression(df)
        # Anomaly Detection
        anomaly_detection(df)
        # Generate summary and prediction
        summary = summarize_findings(df)
        prediction = generate_prediction(summary, st.secrets["API_KEY"])
        st.subheader("Investment Outcome Prediction")
        st.markdown(f"<div style='padding: 10px; border-radius: 10px; background-color: #f0f4c3; margin-bottom: 10px;'>🤖 <strong>Investment predictions response:</strong><br>{prediction}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    app()