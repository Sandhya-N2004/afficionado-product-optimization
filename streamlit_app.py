import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Afficionado Coffee Roasters",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Keep Streamlit's default dark theme, just polish the UI elements ──────────
st.markdown("""
<style>
    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 600;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #C8860A, #6F4E37) !important;
        color: white !important;
    }

    /* ── Metric cards ── */
    [data-testid="metric-container"] {
        border: 1px solid #C8860A44;
        border-radius: 12px;
        padding: 12px;
        box-shadow: 0 4px 15px rgba(200,134,10,0.08);
    }
    [data-testid="metric-container"] label {
        color: #C8860A !important;
        font-size: 12px !important;
        font-weight: 700 !important;
    }

    /* ── Divider ── */
    hr { border-color: #C8860A44 !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PLOT THEME — matches Streamlit dark
# ══════════════════════════════════════════════════════════════════════════════
PLOT_BG  = '#0e1117'
CARD_BG  = '#1c1f26'
GOLD     = '#C8860A'
CREAM    = '#fafafa'

PALETTE  = ['#C8860A','#E8A020','#A0522D','#D2691E','#F4A460',
            '#8B5E3C','#DEB887','#CD853F','#B8860B','#6F4E37']

FMT_USD = mticker.FuncFormatter(lambda x, _: f'${x:,.0f}')
FMT_NUM = mticker.FuncFormatter(lambda x, _: f'{x:,.0f}')

def style_ax(ax, title='', xlabel='', ylabel=''):
    ax.set_facecolor(CARD_BG)
    ax.figure.patch.set_facecolor(PLOT_BG)
    ax.tick_params(colors=CREAM, labelsize=9)
    ax.xaxis.label.set_color(CREAM)
    ax.yaxis.label.set_color(CREAM)
    ax.title.set_color(CREAM)
    for spine in ax.spines.values():
        spine.set_edgecolor('#ffffff11')
    ax.grid(axis='x', color='#ffffff0a', linewidth=0.5)
    if title:  ax.set_title(title, fontweight='bold', color=CREAM, pad=12)
    if xlabel: ax.set_xlabel(xlabel, color=CREAM)
    if ylabel: ax.set_ylabel(ylabel, color=CREAM)

# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
FILE_PATH = 'Afficionado Coffee Roasters.xlsx - Transactions.csv'
@st.cache_data
def load_data():
    df = pd.read_csv(FILE_PATH)
    df = df[(df['transaction_qty'] > 0) & (df['unit_price'] > 0)].copy()
    df['revenue'] = df['transaction_qty'] * df['unit_price']
    return df

df = load_data()
TOTAL_REVENUE = df['revenue'].sum()

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style='text-align:center; padding:20px 0 10px 0;'>
    <h1 style='font-size:40px; color:#C8860A; margin:0; letter-spacing:2px;'>☕ AFFICIONADO COFFEE ROASTERS</h1>
    <p style='color:#aaa; font-size:15px; margin:6px 0 0 0; letter-spacing:1px;'>
        Product Optimization & Revenue Contribution Dashboard
    </p>
</div>
<hr style='border:1px solid #C8860A44; margin:10px 0 20px 0;'>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
st.sidebar.markdown("## ☕ Filters")

all_categories = ['All'] + sorted(df['product_category'].unique().tolist())
selected_cat = st.sidebar.selectbox("🏷️ Product Category", all_categories)

if selected_cat == 'All':
    type_options = ['All'] + sorted(df['product_type'].unique().tolist())
else:
    type_options = ['All'] + sorted(df[df['product_category'] == selected_cat]['product_type'].unique().tolist())
selected_type = st.sidebar.selectbox("🗂️ Product Type", type_options)

all_locations = ['All'] + sorted(df['store_location'].unique().tolist())
selected_loc = st.sidebar.selectbox("🏪 Store Location", all_locations)

top_n = st.sidebar.slider("🔝 Top N Products", min_value=5, max_value=20, value=10)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**📊 Dataset Info**
- Transactions: **149,116**
- Products: **80**
- Stores: **3**
- Categories: **9**
""")

# ── Apply filters ─────────────────────────────────────────────────────────────
df_f = df.copy()
if selected_cat  != 'All': df_f = df_f[df_f['product_category'] == selected_cat]
if selected_type != 'All': df_f = df_f[df_f['product_type']     == selected_type]
if selected_loc  != 'All': df_f = df_f[df_f['store_location']   == selected_loc]

FREV = df_f['revenue'].sum()

# ══════════════════════════════════════════════════════════════════════════════
# AGGREGATIONS
# ══════════════════════════════════════════════════════════════════════════════
popularity = (
    df_f.groupby('product_detail')['transaction_qty']
    .sum().reset_index()
    .rename(columns={'transaction_qty': 'units_sold'})
    .sort_values('units_sold', ascending=False)
    .reset_index(drop=True)
)
popularity['popularity_rank'] = popularity.index + 1

rev_product = (
    df_f.groupby('product_detail')
    .agg(units_sold=('transaction_qty','sum'), total_revenue=('revenue','sum'))
    .reset_index()
    .sort_values('total_revenue', ascending=False)
    .reset_index(drop=True)
)
rev_product['revenue_rank']       = rev_product.index + 1
rev_product['revenue_share_pct']  = (rev_product['total_revenue'] / FREV * 100).round(2)
rev_product['cumulative_rev_pct'] = rev_product['revenue_share_pct'].cumsum().round(2)
rev_product['efficiency_score']   = (rev_product['total_revenue'] / rev_product['units_sold']).round(2)
rev_product = rev_product.merge(popularity[['product_detail','popularity_rank']], on='product_detail')
rev_product['rank_gap'] = rev_product['popularity_rank'] - rev_product['revenue_rank']

med_units   = rev_product['units_sold'].median()
med_revenue = rev_product['total_revenue'].median()

def assign_quadrant(row):
    hi_vol = row['units_sold']    >= med_units
    hi_rev = row['total_revenue'] >= med_revenue
    if   hi_vol and hi_rev:      return 'Hero'
    elif hi_vol and not hi_rev:  return 'Volume Driver'
    elif not hi_vol and hi_rev:  return 'Premium Niche'
    else:                        return 'Underperformer'

rev_product['quadrant'] = rev_product.apply(assign_quadrant, axis=1)

cat_rev = (
    df_f.groupby('product_category')
    .agg(units_sold=('transaction_qty','sum'), total_revenue=('revenue','sum'))
    .reset_index()
    .sort_values('total_revenue', ascending=False)
)
cat_rev['revenue_share_pct'] = (cat_rev['total_revenue'] / FREV * 100).round(2)

hero_count      = (rev_product['quadrant'] == 'Hero').sum()
underp_count    = (rev_product['quadrant'] == 'Underperformer').sum()
top_product     = rev_product.iloc[0]
products_80     = rev_product[rev_product['cumulative_rev_pct'] <= 80].shape[0] + 1
pct_products_80 = round(products_80 / len(rev_product) * 100, 1)
avg_eff_score   = FREV / len(rev_product)
top_cat         = cat_rev.iloc[0]

# ══════════════════════════════════════════════════════════════════════════════
# KPI ROW
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("### 📐 Key Performance Indicators")
c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
c1.metric("💰 Total Revenue",        f"${FREV:,.0f}")
c2.metric("📦 Total SKUs",           f"{len(rev_product)}")
c3.metric("🦸 Hero Products",        f"{hero_count}")
c4.metric("📉 Underperformers",      f"{underp_count}")
c5.metric("🎯 80% Rev Products",     f"{products_80} ({pct_products_80}%)")
c6.metric("💵 Efficiency Score",     f"${avg_eff_score:,.2f}")
c7.metric("🏆 Top Category",         f"{top_cat['product_category']}")
st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs([
    "📊 Popularity", "💰 Revenue", "🔀 Rank Comparison",
    "🏷️ Categories", "📈 Pareto", "🦸 Quadrant", "🏪 Stores"
])

# ── TAB 1 — POPULARITY ────────────────────────────────────────────────────────
with tab1:
    st.markdown("### 📊 Product Popularity — Units Sold")
    col_a, col_b = st.columns(2)

    with col_a:
        top_pop = popularity.head(top_n)
        fig, ax = plt.subplots(figsize=(8, 6))
        norm = plt.Normalize(top_pop['units_sold'].min(), top_pop['units_sold'].max())
        colors = plt.cm.YlOrBr(norm(top_pop['units_sold'][::-1]))
        bars = ax.barh(top_pop['product_detail'][::-1], top_pop['units_sold'][::-1],
                       color=colors, edgecolor=PLOT_BG, linewidth=0.5)
        for bar in bars:
            ax.text(bar.get_width() + top_pop['units_sold'].max()*0.01,
                    bar.get_y()+bar.get_height()/2,
                    f'{bar.get_width():,.0f}', va='center', fontsize=8, color=CREAM)
        style_ax(ax, f'Top {top_n} Products by Units Sold', 'Units Sold')
        ax.xaxis.set_major_formatter(FMT_NUM)
        plt.tight_layout()
        st.pyplot(fig); plt.close()

    with col_b:
        bottom_pop = popularity.tail(10)
        fig, ax = plt.subplots(figsize=(8, 6))
        bars = ax.barh(bottom_pop['product_detail'][::-1], bottom_pop['units_sold'][::-1],
                       color='#c0392b', edgecolor=PLOT_BG, linewidth=0.5)
        for bar in bars:
            ax.text(bar.get_width() + bottom_pop['units_sold'].max()*0.02,
                    bar.get_y()+bar.get_height()/2,
                    f'{bar.get_width():,.0f}', va='center', fontsize=8, color=CREAM)
        style_ax(ax, 'Bottom 10 Products by Units Sold', 'Units Sold')
        plt.tight_layout()
        st.pyplot(fig); plt.close()

    with st.expander("📋 Full Popularity Table"):
        st.dataframe(popularity.style.background_gradient(cmap='YlOrBr', subset=['units_sold']),
                     use_container_width=True)

# ── TAB 2 — REVENUE ───────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 💰 Revenue Contribution Analysis")
    col_a, col_b = st.columns(2)

    with col_a:
        top_rev = rev_product.head(top_n)
        fig, ax = plt.subplots(figsize=(8, 6))
        norm = plt.Normalize(top_rev['total_revenue'].min(), top_rev['total_revenue'].max())
        colors = plt.cm.YlOrBr(norm(top_rev['total_revenue'][::-1]))
        bars = ax.barh(top_rev['product_detail'][::-1], top_rev['total_revenue'][::-1],
                       color=colors, edgecolor=PLOT_BG, linewidth=0.5)
        for bar in bars:
            ax.text(bar.get_width() + top_rev['total_revenue'].max()*0.01,
                    bar.get_y()+bar.get_height()/2,
                    f'${bar.get_width():,.0f}', va='center', fontsize=8, color=CREAM)
        style_ax(ax, f'Top {top_n} Products by Revenue', 'Revenue ($)')
        ax.xaxis.set_major_formatter(FMT_USD)
        plt.tight_layout()
        st.pyplot(fig); plt.close()

    with col_b:
        fig, ax = plt.subplots(figsize=(8, 6))
        sc = ax.scatter(
            rev_product['units_sold'], rev_product['total_revenue'],
            c=rev_product['revenue_share_pct'], cmap='YlOrBr',
            s=80, edgecolors=GOLD, linewidths=0.5, alpha=0.9
        )
        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label('Revenue Share (%)', color=CREAM)
        cbar.ax.yaxis.set_tick_params(color=CREAM)
        plt.setp(cbar.ax.yaxis.get_ticklabels(), color=CREAM)
        for _, row in rev_product.head(5).iterrows():
            ax.annotate(row['product_detail'],
                        xy=(row['units_sold'], row['total_revenue']),
                        xytext=(8, 4), textcoords='offset points',
                        fontsize=7, color=CREAM,
                        arrowprops=dict(arrowstyle='->', color=GOLD, lw=0.8))
        style_ax(ax, 'Popularity vs Revenue Scatter', 'Units Sold', 'Revenue ($)')
        ax.xaxis.set_major_formatter(FMT_NUM)
        ax.yaxis.set_major_formatter(FMT_USD)
        plt.tight_layout()
        st.pyplot(fig); plt.close()

    with st.expander("📋 Full Revenue Table"):
        st.dataframe(
            rev_product[['product_detail','units_sold','total_revenue',
                         'revenue_share_pct','cumulative_rev_pct','efficiency_score','quadrant']]
            .style.background_gradient(cmap='YlOrBr', subset=['total_revenue','revenue_share_pct']),
            use_container_width=True
        )

# ── TAB 3 — RANK COMPARISON ───────────────────────────────────────────────────
with tab3:
    st.markdown("### 🔀 Volume Rank vs Revenue Rank Comparison")
    st.info("💡 **Positive rank gap** = sells a lot but earns less → pricing opportunity. **Negative rank gap** = premium niche product.")

    rank_compare = rev_product[['product_detail','popularity_rank','revenue_rank','rank_gap',
                                 'units_sold','total_revenue','revenue_share_pct']].copy()
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 📦 Volume Leaders Under-earning")
        st.caption("High popularity, low revenue → consider raising prices")
        over = rank_compare[rank_compare['rank_gap'] > 0].sort_values('rank_gap', ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(8, 5))
        norm = plt.Normalize(over['rank_gap'].min(), over['rank_gap'].max())
        colors = plt.cm.Oranges(norm(over['rank_gap'][::-1]))
        ax.barh(over['product_detail'][::-1], over['rank_gap'][::-1],
                color=colors, edgecolor=PLOT_BG)
        style_ax(ax, 'Selling More Than Earning', 'Rank Gap')
        plt.tight_layout()
        st.pyplot(fig); plt.close()

    with col_b:
        st.markdown("#### 💎 Premium Niche — High Revenue, Low Volume")
        st.caption("Low popularity, high revenue → expand marketing")
        under = rank_compare[rank_compare['rank_gap'] < 0].sort_values('rank_gap').head(10)
        fig, ax = plt.subplots(figsize=(8, 5))
        norm = plt.Normalize(under['rank_gap'].abs().min(), under['rank_gap'].abs().max())
        colors = plt.cm.Blues(norm(under['rank_gap'].abs()[::-1]))
        ax.barh(under['product_detail'][::-1], under['rank_gap'].abs()[::-1],
                color=colors, edgecolor=PLOT_BG)
        style_ax(ax, 'Earning More Than Selling', 'Rank Gap (absolute)')
        plt.tight_layout()
        st.pyplot(fig); plt.close()

    with st.expander("📋 Full Rank Comparison Table"):
        st.dataframe(
            rank_compare.sort_values('rank_gap', ascending=False)
            .style.background_gradient(cmap='RdYlGn', subset=['rank_gap']),
            use_container_width=True
        )

# ── TAB 4 — CATEGORIES ────────────────────────────────────────────────────────
with tab4:
    st.markdown("### 🏷️ Category & Product-Type Performance")
    col_a, col_b = st.columns(2)

    with col_a:
        fig, ax = plt.subplots(figsize=(7, 6))
        fig.patch.set_facecolor(PLOT_BG)
        wedges, texts, autotexts = ax.pie(
            cat_rev['total_revenue'],
            labels=cat_rev['product_category'],
            colors=PALETTE[:len(cat_rev)],
            autopct='%1.1f%%', startangle=140,
            wedgeprops={'edgecolor': PLOT_BG, 'linewidth': 2},
            pctdistance=0.82
        )
        for t in texts:     t.set_color(CREAM)
        for a in autotexts: a.set_color('#111'); a.set_fontweight('bold')
        ax.set_facecolor(PLOT_BG)
        ax.set_title('Revenue Share by Category', fontweight='bold', color=CREAM, pad=15)
        plt.tight_layout()
        st.pyplot(fig); plt.close()

    with col_b:
        fig, ax = plt.subplots(figsize=(7, 6))
        norm = plt.Normalize(cat_rev['total_revenue'].min(), cat_rev['total_revenue'].max())
        colors = plt.cm.YlOrBr(norm(cat_rev['total_revenue']))
        bars = ax.bar(cat_rev['product_category'], cat_rev['total_revenue'],
                      color=colors, edgecolor=PLOT_BG, linewidth=0.8, width=0.5)
        for bar in bars:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()*1.02,
                    f'${bar.get_height():,.0f}', ha='center', fontsize=8,
                    color=CREAM, fontweight='bold')
        style_ax(ax, 'Total Revenue by Category', ylabel='Revenue ($)')
        ax.tick_params(axis='x', rotation=25)
        ax.yaxis.set_major_formatter(FMT_USD)
        plt.tight_layout()
        st.pyplot(fig); plt.close()

    st.markdown("#### 🔗 Category Dependence Analysis")
    top3_share = cat_rev.head(3)['revenue_share_pct'].sum()
    top1_share = cat_rev.iloc[0]['revenue_share_pct']
    st.warning(f"⚠️ **'{cat_rev.iloc[0]['product_category']}'** = **{top1_share:.1f}%** of revenue. Top 3 categories = **{top3_share:.1f}%** — high concentration risk.")

    fig, ax = plt.subplots(figsize=(10, 4))
    norm = plt.Normalize(cat_rev['revenue_share_pct'].min(), cat_rev['revenue_share_pct'].max())
    colors = plt.cm.YlOrBr(norm(cat_rev['revenue_share_pct'][::-1]))
    bars = ax.barh(cat_rev['product_category'][::-1], cat_rev['revenue_share_pct'][::-1],
                   color=colors, edgecolor=PLOT_BG)
    ax.axvline(20, color='#e74c3c', linestyle='--', linewidth=1.5, label='20% threshold')
    for bar in bars:
        ax.text(bar.get_width()+0.3, bar.get_y()+bar.get_height()/2,
                f'{bar.get_width():.1f}%', va='center', fontsize=9, color=CREAM)
    style_ax(ax, 'Category Revenue Dependence', 'Revenue Share (%)')
    ax.legend(facecolor=CARD_BG, edgecolor=GOLD, labelcolor=CREAM)
    plt.tight_layout()
    st.pyplot(fig); plt.close()

    with st.expander("📋 Revenue by Product Type"):
        type_rev = (
            df_f.groupby(['product_category','product_type'])
            .agg(units_sold=('transaction_qty','sum'), total_revenue=('revenue','sum'))
            .reset_index().sort_values('total_revenue', ascending=False)
        )
        type_rev['revenue_share_pct'] = (type_rev['total_revenue'] / FREV * 100).round(2)
        st.dataframe(type_rev.style.background_gradient(cmap='YlOrBr', subset=['total_revenue']),
                     use_container_width=True)

# ── TAB 5 — PARETO ────────────────────────────────────────────────────────────
with tab5:
    st.markdown("### 📈 Pareto / 80-20 Revenue Concentration")
    col_info, col_metric = st.columns([3,1])
    with col_info:
        st.info(f"**{products_80} products ({pct_products_80}% of menu) drive 80% of revenue.** The remaining {len(rev_product)-products_80} products share just 20%.")
    with col_metric:
        st.metric("Revenue Concentration Ratio", f"{rev_product.head(5)['revenue_share_pct'].sum():.1f}%", "Top 5 products")

    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax2 = ax1.twinx()
    x = range(len(rev_product))
    norm = plt.Normalize(0, len(rev_product))
    bar_colors = [plt.cm.YlOrBr(1 - norm(i)) for i in x]
    ax1.bar(x, rev_product['revenue_share_pct'], color=bar_colors, alpha=0.9, label='Revenue Share %')
    ax2.plot(x, rev_product['cumulative_rev_pct'], color=GOLD, linewidth=3, label='Cumulative %', zorder=5)
    ax2.fill_between(x, rev_product['cumulative_rev_pct'], alpha=0.08, color=GOLD)
    ax2.axhline(80, color='#e74c3c', linestyle='--', linewidth=2, label='80% threshold')
    ax2.axvline(products_80-1, color='#e74c3c', linestyle=':', linewidth=1.5)
    ax2.annotate(f'  {products_80} products\n  = 80% revenue',
                 xy=(products_80-1, 80), xytext=(products_80+3, 60),
                 arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=1.5),
                 fontsize=10, color='#e74c3c', fontweight='bold')
    for a in [ax1, ax2]:
        a.set_facecolor(CARD_BG)
        a.tick_params(colors=CREAM)
        for spine in a.spines.values(): spine.set_edgecolor('#ffffff11')
    ax1.figure.patch.set_facecolor(PLOT_BG)
    ax1.set_xlabel('Products (ranked by revenue)', color=CREAM)
    ax1.set_ylabel('Individual Revenue Share (%)', color=GOLD)
    ax2.set_ylabel('Cumulative Revenue (%)', color=GOLD)
    ax2.set_ylim(0, 115)
    ax1.set_title(f'Pareto Analysis — {products_80} products ({pct_products_80}% of menu) = 80% of Revenue',
                  fontweight='bold', color=CREAM, pad=12)
    h1,l1 = ax1.get_legend_handles_labels()
    h2,l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1+h2, l1+l2, loc='center right',
               facecolor=CARD_BG, edgecolor=GOLD, labelcolor=CREAM)
    plt.tight_layout()
    st.pyplot(fig); plt.close()

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 🔑 Revenue Anchors")
        st.dataframe(
            rev_product[['product_detail','total_revenue','revenue_share_pct','cumulative_rev_pct']]
            .head(products_80)
            .style.background_gradient(cmap='YlOrBr', subset=['revenue_share_pct']),
            use_container_width=True
        )
    with col_b:
        st.markdown("#### 🐌 Long-tail Products")
        st.dataframe(
            rev_product[['product_detail','total_revenue','revenue_share_pct','cumulative_rev_pct']]
            .tail(len(rev_product)-products_80)
            .style.background_gradient(cmap='Reds', subset=['revenue_share_pct']),
            use_container_width=True
        )

# ── TAB 6 — QUADRANT ──────────────────────────────────────────────────────────
with tab6:
    st.markdown("### 🦸 Hero Products & Quadrant Analysis")

    QCOLORS = {
        'Hero'           : '#27ae60',
        'Premium Niche'  : '#2980b9',
        'Volume Driver'  : '#f39c12',
        'Underperformer' : '#e74c3c'
    }

    selected_quad = st.selectbox("🔍 Highlight Quadrant",
                                  ['All','Hero','Volume Driver','Premium Niche','Underperformer'])

    col_a, col_b = st.columns([2,1])
    with col_a:
        fig, ax = plt.subplots(figsize=(10, 7))
        for quad, grp in rev_product.groupby('quadrant'):
            alpha = 0.9 if (selected_quad == 'All' or selected_quad == quad) else 0.1
            size  = 100 if selected_quad == quad else 65
            ax.scatter(grp['units_sold'], grp['total_revenue'],
                       label=quad, color=QCOLORS[quad],
                       s=size, alpha=alpha, edgecolors='white', linewidths=0.4, zorder=5)
        ax.axvline(med_units,   color=GOLD, linestyle='--', linewidth=1, alpha=0.4)
        ax.axhline(med_revenue, color=GOLD, linestyle='--', linewidth=1, alpha=0.4)
        ax.text(rev_product['units_sold'].max()*0.72, rev_product['total_revenue'].max()*0.92,
                '🦸 HERO', fontsize=10, color='#27ae60', fontweight='bold', alpha=0.5)
        ax.text(rev_product['units_sold'].max()*0.01, rev_product['total_revenue'].max()*0.92,
                '💎 PREMIUM NICHE', fontsize=9, color='#2980b9', fontweight='bold', alpha=0.5)
        ax.text(rev_product['units_sold'].max()*0.72, rev_product['total_revenue'].max()*0.03,
                '📦 VOLUME DRIVER', fontsize=9, color='#f39c12', fontweight='bold', alpha=0.5)
        ax.text(rev_product['units_sold'].max()*0.01, rev_product['total_revenue'].max()*0.03,
                '📉 UNDERPERFORMER', fontsize=9, color='#e74c3c', fontweight='bold', alpha=0.5)
        for _, row in rev_product[rev_product['quadrant']=='Hero'].head(4).iterrows():
            ax.annotate(row['product_detail'],
                        xy=(row['units_sold'], row['total_revenue']),
                        xytext=(8, 5), textcoords='offset points',
                        fontsize=7.5, color=CREAM,
                        arrowprops=dict(arrowstyle='->', color=GOLD, lw=0.8))
        style_ax(ax, 'Product Quadrant Map', 'Total Units Sold', 'Total Revenue ($)')
        ax.xaxis.set_major_formatter(FMT_NUM)
        ax.yaxis.set_major_formatter(FMT_USD)
        ax.legend(loc='upper left', fontsize=9,
                  facecolor=CARD_BG, edgecolor=GOLD, labelcolor=CREAM)
        plt.tight_layout()
        st.pyplot(fig); plt.close()

    with col_b:
        st.markdown("#### Quadrant Summary")
        for quad, color in QCOLORS.items():
            count = (rev_product['quadrant'] == quad).sum()
            st.markdown(f"""
            <div style='border-left:4px solid {color}; border-radius:6px;
                        padding:8px 12px; margin:6px 0; background:rgba(255,255,255,0.03);'>
                <span style='color:{color}; font-weight:700;'>{quad}</span>
                <span style='float:right; font-size:20px; font-weight:800;'>{count}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🦸 Hero Products")
        st.dataframe(
            rev_product[rev_product['quadrant']=='Hero']
            [['product_detail','units_sold','total_revenue','efficiency_score']]
            .sort_values('total_revenue', ascending=False).reset_index(drop=True),
            use_container_width=True
        )

    with st.expander("📉 View Underperformers"):
        st.dataframe(
            rev_product[rev_product['quadrant']=='Underperformer']
            [['product_detail','units_sold','total_revenue','revenue_share_pct','efficiency_score']]
            .sort_values('total_revenue').reset_index(drop=True)
            .style.background_gradient(cmap='Reds', subset=['total_revenue']),
            use_container_width=True
        )

# ── TAB 7 — STORES ────────────────────────────────────────────────────────────
with tab7:
    st.markdown("### 🏪 Store-Level Performance")

    store_rev = (
        df.groupby('store_location')
        .agg(units_sold=('transaction_qty','sum'),
             total_revenue=('revenue','sum'),
             transactions=('transaction_id','nunique'))
        .reset_index()
        .sort_values('total_revenue', ascending=False)
    )
    store_rev['revenue_share_pct']     = (store_rev['total_revenue'] / TOTAL_REVENUE * 100).round(2)
    store_rev['avg_transaction_value'] = (store_rev['total_revenue'] / store_rev['transactions']).round(2)

    scols = st.columns(3)
    scolors = ['#C8860A', '#2980b9', '#27ae60']
    for i, (_, row) in enumerate(store_rev.iterrows()):
        c = scolors[i]
        scols[i].markdown(f"""
        <div style='border:1px solid {c}66; border-radius:12px; padding:16px;
                    text-align:center; background:rgba(255,255,255,0.03);'>
            <div style='color:{c}; font-weight:800; font-size:15px;'>{row['store_location']}</div>
            <div style='font-size:26px; font-weight:800; margin:8px 0;'>${row['total_revenue']:,.0f}</div>
            <div style='color:#aaa; font-size:12px;'>{row['revenue_share_pct']:.1f}% of total revenue</div>
            <div style='color:#aaa; font-size:12px;'>Avg txn: ${row['avg_transaction_value']:.2f}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        fig, ax = plt.subplots(figsize=(7, 5))
        norm = plt.Normalize(store_rev['total_revenue'].min(), store_rev['total_revenue'].max())
        colors = plt.cm.YlOrBr(norm(store_rev['total_revenue']))
        bars = ax.bar(store_rev['store_location'], store_rev['total_revenue'],
                      color=colors, edgecolor=PLOT_BG, width=0.5)
        for bar in bars:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()*1.02,
                    f'${bar.get_height():,.0f}', ha='center', fontsize=9,
                    color=CREAM, fontweight='bold')
        style_ax(ax, 'Total Revenue by Store', ylabel='Revenue ($)')
        ax.yaxis.set_major_formatter(FMT_USD)
        plt.tight_layout()
        st.pyplot(fig); plt.close()

    with col_b:
        fig, ax = plt.subplots(figsize=(7, 5))
        norm = plt.Normalize(store_rev['avg_transaction_value'].min(), store_rev['avg_transaction_value'].max())
        colors = plt.cm.Blues(norm(store_rev['avg_transaction_value']))
        bars = ax.bar(store_rev['store_location'], store_rev['avg_transaction_value'],
                      color=colors, edgecolor=PLOT_BG, width=0.5)
        for bar in bars:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()*1.02,
                    f'${bar.get_height():.2f}', ha='center', fontsize=9,
                    color=CREAM, fontweight='bold')
        style_ax(ax, 'Avg Transaction Value by Store', ylabel='Avg Value ($)')
        plt.tight_layout()
        st.pyplot(fig); plt.close()

    st.markdown("#### 🔥 Revenue Heatmap — Top 15 Products × Store")
    top15 = rev_product.head(15)['product_detail'].tolist()
    heatmap_data = (
        df[df['product_detail'].isin(top15)]
        .groupby(['store_location','product_detail'])['revenue']
        .sum().unstack(fill_value=0)
    )
    fig, ax = plt.subplots(figsize=(16, 4))
    fig.patch.set_facecolor(PLOT_BG)
    ax.set_facecolor(CARD_BG)
    sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlOrBr',
                linewidths=0.5, linecolor=PLOT_BG,
                ax=ax, cbar_kws={'label': 'Revenue ($)'})
    ax.set_title('Revenue Heatmap — Top 15 Products × Store', fontweight='bold', color=CREAM, pad=12)
    ax.tick_params(colors=CREAM)
    ax.set_xlabel('Product', color=CREAM)
    ax.set_ylabel('Store Location', color=CREAM)
    plt.xticks(rotation=40, ha='right', color=CREAM)
    plt.yticks(color=CREAM)
    plt.tight_layout()
    st.pyplot(fig); plt.close()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; padding:10px;'>
    <span style='color:#C8860A;'>☕ Afficionado Coffee Roasters</span>
    <span style='color:#666;'> — Product Optimization & Revenue Contribution Dashboard</span>
</div>
""", unsafe_allow_html=True)
