import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Wonderla Assignment", page_icon="🎢", layout='centered')
st.set_option('deprecation.showPyplotGlobalUse', False)

# Sidebar Navigation
navigation = st.sidebar.radio("Navigation", ["Home", "Data Analysis", "About"])

if navigation == "Home":
    # Home Page with Bigger Logo and Assignment Text
    st.image("Wonderla_Amusements_Parks_Logo.png", width=450, caption='')
    st.markdown("<h4 style='text-align: left; font-family: Arial, sans-serif; font-size: 16px;'>Data Analysis by Shashi Singh</h4>", unsafe_allow_html=True)

elif navigation == "Data Analysis":
    st.subheader("Upload CSV file")
    data_1 = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if data_1 is not None:
        df = pd.read_csv(data_1)  # Read uploaded CSV into DataFrame
        relevant_columns = ['Title', 'Num Of Reviews', 'Average Rating', 'Price', 'Stock', 'Color Category', 'Manufacturer', 'Five Star', 'Four Star', 'Three Star', 'Two Star', 'One Star']
        B = df.loc[:, df.columns.isin(relevant_columns)]
        B['Price'] = B['Price'].replace(',', '', regex=True)
        def convert_price_to_float(x):
            if isinstance(x, str) and ' - ' in x:
                return np.mean([float(i) for i in x.split(' - ')])
            else:
                return float(x) 
        B['Price'] = B['Price'].apply(convert_price_to_float)
        C = B.groupby(['Title']).agg({'Num Of Reviews':'sum', 'Average Rating':'mean', 'Five Star':'sum', 'Four Star':'sum', 'Three Star':'sum', 'Two Star':'sum', 'One Star':'sum', 'Price':'mean'})
        # First Plot: Top 5 Products (based on 'Num Of Reviews') which may not require any promotion/marketing campaign 
        st.subheader("Top 5 Products with Highest Number of Reviews")

        st.write("""
    In this section, we visualize the distribution of star ratings (5 star, 4 star, 3 star, 2 star, and 1 star) among the top 5 products, which are ranked based on the number of reviews they've received.

    The chart provides an insightful view into how these star ratings are distributed across the most-reviewed products in the dataset. This visualization aids in understanding the rating distribution pattern among these top-rated products, offering valuable insights into customer sentiments and product performance.
    """)

        top_5 = C.sort_values(by='Num Of Reviews', ascending=False).head(5)

        # Plotting a stacked bar chart for the top 5 products based on different star ratings
        plt.figure(figsize=(10, 6))
        top_5[['Five Star', 'Four Star', 'Three Star', 'Two Star', 'One Star']].plot(kind='bar', stacked=True)
        plt.xlabel('Product Titles')
        plt.ylabel('Number of Reviews')
        plt.title('Star Rating Distribution of Top 5 Products')
        plt.xticks(rotation=45, ha='right')
        plt.legend(loc='upper right')
        plt.tight_layout()


        st.pyplot()  
       
        st.subheader("Products Requiring Promotion/Marketing")

        #Not considering products which dont have any reviews
        D = C[C['Num Of Reviews'] != 0.0]
        D['% of Good Ratings'] = ((D['Five Star'] + D['Four Star'])/D['Num Of Reviews'])*100
        # Calculate the score based on the given criteria
        def calculate_promotion_score(row):
            good_ratings = row['% of Good Ratings']
            
            if good_ratings >= 90:
                good_ratings_score = 5
            elif 70 <= good_ratings < 90:
                good_ratings_score = 4
            elif 50 <= good_ratings < 70:
                good_ratings_score = 3
            elif 30 <= good_ratings < 50:
                good_ratings_score = 2
            elif 10 <= good_ratings < 30:
                good_ratings_score = 1
            else:
                good_ratings_score = 0

            num_of_reviews = row['Num Of Reviews']
            if num_of_reviews >= D['Num Of Reviews'].quantile(0.75):
                num_of_reviews_score = 2
            elif num_of_reviews >= D['Num Of Reviews'].quantile(0.5):
                num_of_reviews_score = 3
            elif num_of_reviews >= D['Num Of Reviews'].quantile(0.25):
                num_of_reviews_score = 4
            else:
                num_of_reviews_score = 5

            return good_ratings_score + num_of_reviews_score


        # Apply the function to create a new 'Promotion Score' column
        D['Promotion Score'] = D.apply(calculate_promotion_score, axis=1)
        filtered_df = D[D['Promotion Score'] > D['Promotion Score'].mean()].sort_values(by = '% of Good Ratings', ascending = False)
        st.write("""
        To identify products that would require marketing/promotions, I've developed two logics that generally hold true in most cases.

        **Logic 1: Scoring Products for Promotion**
        Here, I've devised a scoring system based on two significant factors:

        1- **High Percentage of Positive Ratings:**
        A product with a high '% of Good Ratings' [(Count of 5-star + Count of 4-star) / (Num Of Reviews)] indicates that the product is of high quality and holds substantial potential.

        2- **Low Number of Reviews:**
        Lower counts of 'Num Of Reviews' suggest that the product hasn't gained much popularity, possibly due to an absence of an effective marketing campaign.
        """)

        st.write(filtered_df.head(10))

        # Function to identify products with potential marketing campaign issues based on ratings distribution
        def detect_misleading_marketing(row):
            # Extracting the ratings columns
            ratings = row[['Five Star', 'Four Star', 'Three Star', 'Two Star', 'One Star']]
            
            # Calculate the sum of ratings
            total_ratings = ratings.sum()
            
            # Calculate the percentage of low ratings (1-star and 2-star ratings)
            low_ratings_percentage = ((ratings['One Star'] + ratings['Two Star']) / total_ratings * 100) if total_ratings > 0 else 0
            
            # If the percentage of low ratings is higher than a threshold, flag it as a potential issue
            if low_ratings_percentage > 50:  # You can adjust the threshold percentage as needed
                return True
            else:
                return False

        # Apply the function to each row in the dataframe to identify products with potential issues in the marketing campaign
        C['Potential Issue'] = C.apply(detect_misleading_marketing, axis=1)
        #These products which may require a new marketing campaign/promotional strategy.
        filtered_df_2 = C[C['Potential Issue'] == True].sort_values(by = ['Num Of Reviews'], ascending = False)
        st.write("""
        To flag potential marketing issues in products, I've established a second logic that revolves around examining their ratings distribution, especially focusing on 1-star and 2-star ratings.

        **Logic 2: Identifying Potential Marketing Issues**
        This logic is designed to spot products with potential marketing concerns by scrutinizing their ratings distribution.

        The rationale behind this assessment:
        - Products accumulating a significant count of 1-star and 2-star ratings (representing more than 50% of total ratings) might indicate a discrepancy between customer expectations set by marketing and the actual product experience.

        This logic helps identify products that might face challenges with their marketing content, suggesting a need for revisiting marketing strategies or improving the product for enhanced customer satisfaction.
        """)

        st.write(filtered_df_2.head(10))
        
        st.subheader("Distress Identification: Pinpointing Buyer Discontent")

        """
        Here, I will focus on identifying product categories causing distress amongst the buyers.
        The logic behind the analysis:
        Products with more 1 star and 2 star ratings when compared to 3 star, 4 star and 5 star ratings are considered to cause concern among consumers. 
        A high number of low ratings tells us that most of the customers face issue and are dissatisfied.
        """


        C['Total Ratings'] = C[['Five Star', 'Four Star', 'Three Star', 'Two Star', 'One Star']].sum(axis=1)
        C['Low Ratings %'] = ((C['One Star'] + C['Two Star']) / C['Total Ratings']) * 100
        filtered_df_3 = C[C['Low Ratings %'] > 80].sort_values(by = 'Num Of Reviews', ascending = False)
        st.write(filtered_df_3.head(10))

        st.subheader("Pricing and Review Impact: Analyzing Pricing and Review Correlation")

        """
            This analysis aims to identify correlations between various features using heatmap visualizations for easy interpretation.

            Correlation values near 1 indicate a strong relationship between two features, where changes in one feature significantly influence changes in the other and vice versa. Conversely, a correlation value below 0.5 suggests a weak correlation, implying that one feature has no substantial impact on the other and is relatively independent.
            """


        missing_percentage = (C['Price'].isnull().sum() / C['Price'].notnull().sum()) * 100

        message = f"We can see that around {missing_percentage:.2f}% of the data is missing for the 'Price' column. Here I am only considering cases where 'Price' column has data."
        st.write(message)
        E = C[C['Price'].isnull() == False]
        columnsforcorr = ['Num Of Reviews', 'Average Rating', 'Five Star', 'Four Star', 'Three Star', 'Two Star', 'One Star', 'Price']
        correlation_matrix = E[columnsforcorr].corr()
        import matplotlib.pyplot as plt
        import seaborn as sns

        plt.figure(figsize=(8, 6))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.4f')
        plt.title('Correlation Heatmap: Pricing vs. Reviews')
        plt.tight_layout()
        st.pyplot()  

        E[columnsforcorr].corr().unstack().abs().sort_values(ascending = False) [E[columnsforcorr].corr().unstack().abs().sort_values(ascending = False).index.get_level_values(0) !=E[columnsforcorr].corr().unstack().abs().sort_values(ascending = False).index.get_level_values(1)]

        st.subheader("Buyer's Perspective: Criteria for Product Selection")

        """
        This section mirrors a buyer's mindset when selecting products across different categories. It focuses on essential factors influencing their decisions:

        1. **Quality-Oriented Choices:** Preference for products with high average ratings and a substantial number of reviews to ensure reliability and quality.
        2. **Avoidance of Low-Rated or Under-Reviewed Products:** Products with fewer ratings or reviews are avoided due to potential credibility issues.
        3. **Budget Constraints:** Adherence to budget limitations is vital, guiding the selection process and preventing overspending.
        4. **Consideration for Exceptional Products:** Products with fewer reviews but exceptionally high ratings might still be considered for their outstanding performance.

        Creating a Selection Scoring Mechanism:
        To streamline decision-making, a scoring mechanism incorporates three primary factors:
        1. **Average Rating:** Given higher priority, emphasizing superior-rated products.
        2. **Number of Reviews:** Indicates comfort with higher-reviewed products.
        3. **Budget Threshold:** Maintaining a specified budget limit (e.g., $200).

        The 'Score' column, derived from these factors, helps identify products aligned with the buyer's preferences. The resulting data showcases products meeting these criteria while adhering to the specified budget.
        """

            
        def calculate_score(row, budget):
                weight_rating = 0.5
                weight_reviews = 0.4
                
                avg_rating = row['Average Rating']
                num_reviews = row['Num Of Reviews']
                price = row['Price']
                
                # Calculate the score based on the defined weights and parameters
                score = (weight_rating * avg_rating) + (weight_reviews * num_reviews)
                
                return score

        # Set the budget (maximum price)
        budget_limit = 200  # Modify this value according to your budget

        # Apply the scoring function to create a 'Score' column in the dataframe
        D['Score'] = D.apply(lambda row: calculate_score(row, budget_limit), axis=1)

        # Filter products within the specified budget and sort them by the calculated score
        products_within_budget = D[D['Price'] <= budget_limit].sort_values(by='Score', ascending=False)

        # Display the recommended products within the budget
        products_within_budget

        st.subheader("Marketing Insights: Analyzing Product Ratings and Reviews for Marketing Strategies")

        """
        This section delves into the realm of marketing insights by harnessing product-related data to derive valuable insights instrumental in shaping marketing strategies and decisions.

        **Data Preprocessing:**
        Relevant columns crucial for marketing analysis are extracted, including attributes like 'Title', 'Num Of Reviews', 'Average Rating', 'Price', 'Stock', 'Color Category', 'Manufacturer', and individual star ratings ('Five Star', 'Four Star', 'Three Star', 'Two Star', 'One Star'). The 'Price' column undergoes preprocessing, standardizing its format and converting it to float values for accurate analysis.

        **Aggregating Insights:**
        Grouping the data by product titles ('Title'), essential metrics are aggregated, encompassing cumulative reviews ('Num Of Reviews'), average ratings ('Average Rating'), and total counts for individual star ratings. This structured dataset provides a comprehensive overview of product performance, aiding in deriving actionable marketing insights.

        **Analyzing Rating Distribution:**
        A histogram showcasing the distribution of average ratings is plotted, excluding products with a 0 rating. This visualization enables a deeper understanding of the frequency distribution of ratings across different products.

        **Review Distribution by Rating:**
        A bar chart depicting the total number of reviews corresponding to each star rating (One Star to Five Star) is presented. This visualization offers a clear depiction of the volume of reviews received across various rating categories, providing insights into customer sentiments and preferences.

        These visualizations and data aggregations serve as pivotal resources for marketing professionals and stakeholders, offering a comprehensive understanding of product performance, customer satisfaction, and areas warranting marketing attention or enhancement.
        """


        relevant_columns = ['Title', 'Num Of Reviews', 'Average Rating', 'Price', 'Stock', 'Color Category', 'Manufacturer', 'Five Star', 'Four Star', 'Three Star', 'Two Star', 'One Star']
        B = df.loc[:, df.columns.isin(relevant_columns)]
        B['Price'] = B['Price'].replace(',', '', regex=True)
        def convert_price_to_float(x):
            if isinstance(x, str) and ' - ' in x:
                return np.mean([float(i) for i in x.split(' - ')])
            else:
                return float(x) 
        B['Price'] = B['Price'].apply(convert_price_to_float)
        C = B.groupby(['Title']).agg({'Num Of Reviews':'sum', 'Average Rating':'mean', 'Five Star':'sum', 'Four Star':'sum', 'Three Star':'sum', 'Two Star':'sum', 'One Star':'sum', 'Price':'mean'})
        C = C.reset_index()
        
        filtered_data = C[C['Average Rating'] > 0]['Average Rating']

        plt.figure(figsize=(8, 6))
        plt.hist(filtered_data, bins=10, edgecolor='black')
        plt.xlabel('Average Rating')
        plt.ylabel('Frequency')
        plt.title('Histogram of Average Ratings (Excluding 0 Ratings)')
        plt.grid(True)
        st.pyplot()


        ratings = ['One Star', 'Two Star', 'Three Star', 'Four Star', 'Five Star']
        num_reviews = [C['One Star'].sum(), C['Two Star'].sum(), C['Three Star'].sum(), C['Four Star'].sum(), C['Five Star'].sum()]

        plt.figure(figsize=(10, 6))
        plt.bar(ratings, num_reviews, color='skyblue')
        plt.xlabel('Rating')
        plt.ylabel('Number of Reviews')
        plt.title('Number of Reviews by Rating')
        plt.grid(axis='y')
        st.pyplot()


elif navigation == "About":
    st.markdown("<h3>About</h3>", unsafe_allow_html=True)
    st.write("Thanks for visiting my assignment.")

    contact_details = """
    <div style="background-color: #f0f0f0; padding: 8px; border-radius: 5px; width: 550px;">
        <h4 style="font-size: 14px;">Contact Details:</h4>
        <ul style="list-style-type: none; padding-left: 0; font-size: 13px;">
            <li>Shashi Singh</li>
            <li>Data Scientist, Sundaram Finance </li>
            <li>IIT Dhanbad Alumnus</li>
            <li><strong>Email:</strong> datascientistshashi@gmail.com</li>
            <li><strong>Phone:</strong> 9025734889</li>
            <li><strong>LinkedIn:</strong> <a href="https://www.linkedin.com/in/shashiiit/">LinkedIn Profile</a></li>
            <li><strong>GitHub:</strong> <a href="https://github.com/Shashi503">GitHub Profile</a></li>
        </ul>
    </div>
    """

    # Displaying an animated GIF (example)
    

    # Elevate the about section with additional content
    st.markdown("<h4>Background</h4>", unsafe_allow_html=True)
    st.write("I am a passionate Data Scientist with a strong background in machine learning and data analysis. "
             "During my time at IIT Dhanbad and Sundaram Finance, I focused on learning and exploring cutting-edge technologies and solutions "
             "in the field of data science.")

    


    # Display contact details
    st.markdown(contact_details, unsafe_allow_html=True)
