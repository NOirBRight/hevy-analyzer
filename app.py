import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
import html
import urllib.parse

# 获取应用程序所在目录（支持打包后的EXE和直接运行的脚本）
if getattr(sys, 'frozen', False):
    # 作为打包后的可执行文件运行
    APP_DIR = Path(sys.executable).parent
else:
    # 作为脚本运行
    APP_DIR = Path(__file__).parent

try:
    from streamlit_float import float_init  # type: ignore
    STREAMLIT_FLOAT_READY = True
except ImportError:  # pragma: no cover - optional dependency
    float_init = None
    STREAMLIT_FLOAT_READY = False


st.set_page_config(
    page_title="Hevy Analyzer",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

if STREAMLIT_FLOAT_READY and float_init is not None:
    float_init(theme=False)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] button {
        text-align: left;
        justify-content: flex-start;
    }
    [data-testid="stSidebar"] button:hover {
        background: rgba(255, 255, 255, 0.08);
    }
    [data-testid="stSidebar"] button p {
        text-align: left;
    }
    .sidebar-brand {
        font-weight: 700;
        font-size: 1.25rem;
        letter-spacing: 0.08em;
        margin-bottom: 1.5rem;
    }
    .sidebar-note {
        font-size: 0.8rem;
        color: #8b93a7 !important;
        margin-bottom: 1.5rem;
    }
    .sidebar-nav-active {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        background: rgba(79, 123, 255, 0.25);
        box-shadow: inset 0 0 0 1px rgba(79, 123, 255, 0.45);
        padding: 0.65rem 0.85rem;
        border-radius: 12px;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }
    .sidebar-nav-active .icon {
        font-size: 1.15rem;
    }
    :root {
        --hevy-main-width: min(960px, calc(100vw - 32px));
        --hevy-main-left: 16px;
    }
    [data-testid="stAppViewContainer"] [data-testid="block-container"],
    [data-testid="stAppViewContainer"] .block-container {
        max-width: min(1180px, calc(100vw - 48px));
        margin-left: auto;
        margin-right: auto;
        padding-left: 1.25rem;
        padding-right: 1.25rem;
        /* Reduce top padding so content starts closer to the top */
        padding-top: 1rem !important;
        padding-bottom: 1.5rem !important;
        width: 100%;
        box-sizing: border-box;
    }
    .toolbar-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #8a8f9c;
        margin-bottom: 0.2rem;
    }
    div[data-testid="stSidebar"] input {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: #f5f6fa !important;
        border-radius: 12px;
    }
    [data-testid="stSidebar"] input:focus {
        border-color: rgba(79, 123, 255, 0.95);
        box-shadow: 0 0 0 1px rgba(79, 123, 255, 0.45);
    }
    [data-testid="stSidebar"] label {
        color: #9aa3bd !important;
    }
    [data-testid="stSidebar"] div[data-testid="stNumberInput"] label,
    [data-testid="stSidebar"] div[data-testid="stNumberInput"] label span {
        color: #9aa3bd !important;
    }
    [data-testid="stSidebar"] div[data-testid="stNumberInput"] input {
        background: rgba(255, 255, 255, 0.92);
        color: #111111 !important;
        border: none;
    }
    [data-testid="stSidebar"] div[data-testid="stNumberInput"] input:focus {
        background: #ffffff;
        color: #000000 !important;
    }
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] input,
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.92) !important;
        color: #111111 !important;
        border: none !important;
    }
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] input:focus,
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within > div {
        background: #ffffff !important;
        color: #000000 !important;
    }
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] label {
        color: #9aa3bd !important;
    }
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] [role="button"] span,
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] [role="option"],
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] div[role="button"] > div,
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] [class*="StyledSingleValue"] {
        color: #111111 !important;
    }
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] [role="option"]:hover {
        color: #000000 !important;
    }
    /* Force text content in selectbox value area to be dark, but not the label */
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] * {
        color: #111111 !important;
    }
    .fetch-overlay {
        position: fixed;
        inset: 0;
        background: rgba(8, 12, 22, 0.88);
        z-index: 9999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.75rem;
        color: #f5f6fa;
        font-size: 1.1rem;
        font-weight: 500;
    }
    .fetch-overlay .spinner {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        border: 3px solid rgba(255, 255, 255, 0.18);
        border-top-color: rgba(79, 123, 255, 0.9);
        animation: spin 0.8s linear infinite;
    }
    .fetch-overlay .log-line {
        font-size: 0.85rem;
        color: rgba(245, 246, 250, 0.82);
    }
    .fetch-overlay .log-line strong {
        color: #f5f6fa;
    }
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    main h1 {
        margin-bottom: 0.35rem;
    }
    header[data-testid="stHeader"] {
        display: none;
    }
    .hevy-sidebar-toggle {
        position: fixed;
        top: 18px;
        left: 18px;
        border: none;
        background: transparent;
        color: rgba(11, 15, 24, 0.75);
        padding: 0;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 5000;
        transition: color 0.2s ease, transform 0.15s ease, filter 0.2s ease;
    }
    .hevy-sidebar-toggle:hover {
        color: rgba(79, 123, 255, 0.95);
        filter: drop-shadow(0 2px 4px rgba(79, 123, 255, 0.3));
        transform: translateX(2px);
    }
    .hevy-sidebar-toggle .icon {
        font-size: 2rem;
        line-height: 1;
        filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.2));
        transition: transform 0.3s ease;
        font-family: 'Material Symbols Rounded';
        font-weight: 400;
        font-style: normal;
    }
    .hevy-sidebar-toggle.sidebar-expanded .icon {
        transform: rotate(180deg);
    }
    .data-source-actions {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-top: 0.75rem;
        gap: 0.4rem;
    }
    .data-source-actions .stButton > button {
        min-width: 160px;
        border-radius: 999px;
    }
    .data-source-chip button {
        background: #ffffff;
        color: #0b0f18;
        border-radius: 999px;
        border: 1px solid rgba(11, 15, 24, 0.12);
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
        padding: 0.4rem 1.1rem;
        font-weight: 600;
        min-width: 260px;
        white-space: nowrap;
    }
    .data-source-chip button:hover {
        border-color: rgba(79, 123, 255, 0.35);
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.18);
    }
    .data-source-panel-wrapper {
        position: fixed;
        bottom: 120px;
        right: 32px;
        width: 360px;
        z-index: 1500;
    }
    .data-source-panel {
        background: #ffffff;
        border-radius: 24px;
        padding: 1.35rem 1.5rem 1.75rem;
        box-shadow: 0 18px 40px rgba(12, 18, 34, 0.2);
        border: 1px solid rgba(11, 15, 24, 0.08);
    }
    .data-source-panel h4 {
        margin-bottom: 0.25rem;
    }
    .data-source-panel-close .stButton > button {
        border-radius: 999px;
        width: 100%;
    }
    .floating-controls-panel-wrapper {
        position: fixed;
        bottom: 20px;
        left: calc(
            var(--hevy-main-left, 16px) +
            var(--hevy-main-width, min(960px, calc(100vw - 32px))) / 2
        );
        transform: translateX(-50%);
        width: var(--hevy-main-width, min(960px, calc(100vw - 32px)));
        max-width: min(1180px, calc(100vw - 32px));
        z-index: 1450;
    }
    .floating-controls-panel {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 26px;
        padding: 1rem 1.2rem;
        box-shadow: 0 30px 60px rgba(12, 18, 34, 0.25);
        border: 1px solid rgba(15, 23, 42, 0.08);
    }
    .floating-toolbar-grid {
        width: 100%;
    }
    .floating-toolbar-item {
        background: linear-gradient(180deg, #f9faff, #f1f3fb);
        border-radius: 18px;
        padding: 0.6rem 0.85rem 0.75rem;
        border: 1px solid rgba(15, 23, 42, 0.08);
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.7), 0 12px 26px rgba(12, 18, 34, 0.12);
        height: 100%;
    }
    .floating-toolbar-item.tight {
        padding: 0.55rem 0.75rem 0.65rem;
    }
    .floating-panel-content {
        padding: 0;
        width: 100%;
        overflow: visible;
    }
    .floating-section-label {
        font-size: 0.62rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #5b6276;
        margin-bottom: 0.35rem;
        font-weight: 700;
    }
    .floating-source-summary {
        font-size: 0.7rem;
        color: #5c647a;
        margin-bottom: 0.25rem;
    }
    .floating-source-name {
        font-weight: 700;
        font-size: 0.78rem;
        margin-bottom: 0.12rem;
        line-height: 1.1;
        word-break: break-word;
    }
    .floating-controls-panel div[data-testid="stSelectbox"] label {
        display: none !important;
    }
    .floating-controls-panel div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        border-radius: 10px !important;
        border: 1px solid rgba(11, 15, 24, 0.18) !important;
        background: #f7f8fb !important;
        min-height: 34px;
        box-shadow: inset 0 0 0 1px rgba(11, 15, 24, 0.04);
    }
    .floating-controls-panel div[data-testid="stSelectbox"] [role="listbox"] {
        border-radius: 16px !important;
        border: 1px solid rgba(11, 15, 24, 0.12) !important;
        box-shadow: 0 18px 44px rgba(12, 18, 34, 0.24) !important;
    }
    .floating-controls-panel div[data-testid="stSelectbox"] [class*="SingleValue"] {
        color: #0b0f18 !important;
        font-weight: 600;
        font-size: 0.78rem;
    }
    .floating-controls-panel .stButton > button {
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.72rem;
        height: 34px;
        background: linear-gradient(120deg, rgba(74,114,255,0.95), rgba(126,90,255,0.95));
        border: none;
        color: #ffffff;
        box-shadow: 0 12px 26px rgba(74, 114, 255, 0.35);
    }
    .floating-controls-panel .stButton > button:focus {
        outline: none;
        box-shadow: 0 12px 26px rgba(74, 114, 255, 0.5);
    }
    .floating-inline-select-shell {
        position: relative;
        border-radius: 14px;
        border: 1px solid rgba(11, 15, 24, 0.12);
        background: #fdfdff;
        box-shadow: 0 12px 26px rgba(12, 18, 34, 0.12);
        padding: 0.45rem 0.55rem 0.25rem;
        margin-bottom: 0;
        width: 100%;
        box-sizing: border-box;
    }
    .floating-inline-select-shell.no-label {
        padding: 0.35rem 0.6rem 0.35rem;
    }
    .floating-inline-select-shell:focus-within {
        border-color: rgba(74, 114, 255, 0.65);
        box-shadow: 0 0 0 2px rgba(74, 114, 255, 0.16);
        background: #ffffff;
    }
    .floating-inline-select-label {
        position: absolute;
        top: 0.25rem;
        left: 0.6rem;
        font-size: 0.54rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #8a8fa4;
        pointer-events: none;
        font-weight: 600;
    }
    .floating-inline-select-shell.no-label .floating-inline-select-label {
        display: none;
    }
    .floating-panel-test-select {
        width: 100%;
        border: none;
        background: transparent;
        padding: 0.6rem 1.4rem 0.1rem 0;
        font-weight: 600;
        font-size: 0.78rem;
        color: #0b0f18;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        appearance: none;
        -webkit-appearance: none;
        -moz-appearance: none;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24'%3E%3Cpath fill='none' stroke='%230b0f18' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: right 0.05rem center;
        background-size: 9px 9px;
    }
    .floating-panel-test-select:focus {
        outline: none;
    }
    .floating-panel-test-select option {
        font-weight: 600;
        font-size: 0.78rem;
        background: #ffffff;
        color: #0b0f18;
    }
    .floating-panel-test-select::-ms-expand {
        display: none;
    }
    .floating-period-nav {
        width: 100%;
    }
    .floating-period-nav .stButton > button {
        width: 100%;
        border-radius: 12px;
        border: 1px solid rgba(11, 15, 24, 0.1);
        background: #eef1ff;
        color: #18203a;
        font-weight: 700;
        height: 40px;
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.8);
    }
    .floating-period-nav .stButton > button:disabled {
        opacity: 0.45;
        background: #f0f2f8;
    }
    .floating-period-select {
        width: 100%;
    }
    .floating-period-value {
        margin-top: 0.35rem;
        font-size: 0.72rem;
        font-weight: 600;
        color: #4d5673;
        letter-spacing: 0.04em;
    }
    .floating-manage-button .stButton > button {
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.74rem;
        height: 38px;
        background: linear-gradient(120deg, rgba(74,114,255,0.95), rgba(126,90,255,0.95));
        border: none;
        color: #ffffff;
        box-shadow: 0 12px 26px rgba(74, 114, 255, 0.35);
    }
    .floating-manage-button .stButton > button:focus {
        outline: none;
        box-shadow: 0 12px 26px rgba(74, 114, 255, 0.5);
    }
    .data-source-dropdown-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #7b8196;
        margin-bottom: 0.4rem;
    }
    .data-source-dropdown {
        border-radius: 18px;
        background: #f8f9fb;
        padding: 0.15rem 0.45rem 0.45rem;
        box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.08);
    }
    .data-source-dropdown div[data-baseweb="select"] > div {
        border-radius: 14px !important;
        border: 1px solid rgba(15, 23, 42, 0.12) !important;
        background: #ffffff !important;
        box-shadow: 0 10px 24px rgba(12, 18, 34, 0.12) !important;
        min-height: 48px;
    }
    .data-source-dropdown div[data-baseweb="select"] span {
        color: #0b0f18 !important;
        font-weight: 600;
    }
    .data-source-dropdown div[data-baseweb="select"] [role="listbox"] {
        margin-top: 0.35rem;
        border-radius: 18px;
        border: 1px solid rgba(11, 15, 24, 0.12);
        box-shadow: 0 22px 45px rgba(12, 18, 34, 0.22);
    }
    [data-testid="stSidebar"][aria-expanded="true"] {
        width: 280px;
        min-width: 280px;
        border: none;
        box-shadow: none;
    }
    [data-testid="stSidebar"][aria-expanded="false"] {
        width: 0 !important;
        min-width: 0 !important;
        border: none;
        box-shadow: none;
    }
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebarNav"] > div:first-child {
        border: none !important;
        box-shadow: none !important;
    }
    .sidebar-nav-active {
        margin-bottom: 0.6rem;
        border-radius: 12px;
    }
    [data-testid="stSidebar"] input:focus {
        border-color: rgba(79, 123, 255, 0.95);
        box-shadow: 0 0 0 1px rgba(79, 123, 255, 0.45);
    }
    [data-testid="stSidebar"] label {
        color: #9aa3bd !important;
    }
    [data-testid="stSidebar"] div[data-testid="stNumberInput"] label,
    [data-testid="stSidebar"] div[data-testid="stNumberInput"] label span {
        color: #9aa3bd !important;
    }
    [data-testid="stSidebar"] div[data-testid="stNumberInput"] input {
        background: rgba(255, 255, 255, 0.92);
        color: #111111 !important;
        border: none;
    }
    [data-testid="stSidebar"] div[data-testid="stNumberInput"] input:focus {
        background: #ffffff;
        color: #000000 !important;
    }
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] input,
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.92) !important;
        color: #111111 !important;
        border: none !important;
    }
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] input:focus,
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within > div {
        background: #ffffff !important;
        color: #000000 !important;
    }
    /* Selectbox label should stay light colored */
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] label {
        color: #9aa3bd !important;
    }
    /* Selectbox selected value and dropdown options should be dark */
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] [role="button"] span,
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] [role="option"],
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] div[role="button"] > div,
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] [class*="StyledSingleValue"] {
        color: #111111 !important;
    }
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] [role="option"]:hover {
        color: #000000 !important;
    }
    /* Force text content in selectbox value area to be dark, but not the label */
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] * {
        color: #111111 !important;
    }
    .fetch-overlay {
        position: fixed;
        inset: 0;
        background: rgba(8, 12, 22, 0.88);
        z-index: 999999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.75rem;
        color: #f5f6fa;
        font-size: 1.1rem;
        font-weight: 500;
    }
    .fetch-overlay .spinner {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        border: 3px solid rgba(255, 255, 255, 0.18);
        border-top-color: rgba(79, 123, 255, 0.9);
        animation: spin 0.8s linear infinite;
    }
    .fetch-overlay .log-line {
        font-size: 0.85rem;
        color: rgba(245, 246, 250, 0.82);
    }
    .fetch-overlay .log-line strong {
        color: #f5f6fa;
    }
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    main h1 {
        margin-bottom: 0.35rem;
    }
    /* Hide Streamlit toolbar */
    header[data-testid="stHeader"] {
        display: none;
    }
    div[data-testid="stExpander"] > details {
        border: 1px solid rgba(11, 15, 24, 0.12);
        border-radius: 18px;
        background: #ffffff;
        color: #111111;
        box-shadow: 0 10px 25px rgba(5, 10, 30, 0.12);
    }
    div[data-testid="stExpander"] > details > summary {
        font-weight: 600;
        font-size: 0.9rem;
        color: #0b0f18;
    }
    div[data-testid="stExpander"] p,
    div[data-testid="stExpander"] label,
    div[data-testid="stExpander"] span,
    div[data-testid="stExpander"] .markdown-text-container * {
        color: #0b0f18 !important;
    }
    .data-source-actions {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-top: 0.75rem;
    }
    .data-source-actions .stButton > button {
        min-width: 160px;
        border-radius: 999px;
    }
    .data-source-chip button {
        background: #ffffff;
        color: #0b0f18;
        border-radius: 999px;
        border: 1px solid rgba(11, 15, 24, 0.12);
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
        padding: 0.4rem 1.1rem;
        font-weight: 600;
        min-width: 260px;
        white-space: nowrap;
    }
    .data-source-chip button:hover {
        border-color: rgba(79, 123, 255, 0.35);
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.18);
    }
    .data-source-panel-wrapper {
        position: fixed;
        bottom: 120px;
        right: 32px;
        width: min(420px, calc(100% - 48px));
        z-index: 1500;
    }
    .data-source-panel {
        background: #ffffff;
        border-radius: 24px;
        padding: 1.35rem 1.5rem 1.75rem;
        box-shadow: 0 18px 40px rgba(12, 18, 34, 0.2);
        border: 1px solid rgba(11, 15, 24, 0.08);
    }
    .data-source-panel h4 {
        margin-bottom: 0.25rem;
    }
    .data-source-panel-close .stButton > button {
        border-radius: 999px;
        width: 100%;
    }
    [data-testid="stSidebar"] {
        width: 280px;
        min-width: 280px;
        border: none;
        box-shadow: none;
    }
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebarNav"] > div:first-child {
        border: none !important;
        box-shadow: none !important;
    }
    .sidebar-nav-active {
        margin-bottom: 0.6rem;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def mount_sidebar_toggle_button() -> None:
    components.html(
        """
        <script>
        (function() {
            const doc = window.parent && window.parent.document ? window.parent.document : document;
            if (!doc) {
                return;
            }

            const previous = doc.getElementById("hevy-sidebar-toggle");
            if (previous) {
                previous.remove();
            }

            const toggleButton = doc.createElement("button");
            toggleButton.id = "hevy-sidebar-toggle";
            toggleButton.type = "button";
            toggleButton.className = "hevy-sidebar-toggle";
            toggleButton.setAttribute("aria-label", "Toggle sidebar");
            toggleButton.innerHTML = '<span class="icon material-symbols-rounded">keyboard_double_arrow_left</span>';

            const findNativeToggle = () =>
                doc.querySelector('[data-testid="collapsedControl"] button') ||
                doc.querySelector('[data-testid="stSidebarCollapseButton"] button') ||
                doc.querySelector('button[aria-label="Toggle sidebar"]') ||
                doc.querySelector('button[aria-label="Show sidebar"]') ||
                doc.querySelector('button[aria-label="Hide sidebar"]') ||
                doc.querySelector('button[title="Toggle sidebar"]') ||
                doc.querySelector('button[title="Hide sidebar"]');

            const triggerSidebarToggle = (forceExpand = false) => {
                const nativeToggle = findNativeToggle();
                if (nativeToggle) {
                    if (forceExpand) {
                        const expandedAttr = nativeToggle.getAttribute('aria-expanded');
                        if (expandedAttr === 'true') {
                            return true;
                        }
                        if (expandedAttr === null) {
                            const currentExpanded = doc.querySelector('[data-testid="stSidebar"][aria-expanded="true"]');
                            if (currentExpanded) {
                                return true;
                            }
                        }
                    }
                    nativeToggle.click();
                    return true;
                }

                const event = new KeyboardEvent("keydown", {
                    key: "b",
                    code: "KeyB",
                    keyCode: 66,
                    ctrlKey: true,
                    bubbles: true,
                });
                doc.dispatchEvent(event);
                window.parent && window.parent.dispatchEvent && window.parent.dispatchEvent(event);
                return false;
            };

            const updateButtonState = () => {
                const sidebar = doc.querySelector('[data-testid="stSidebar"]');
                if (!sidebar) {
                    return;
                }
                const computed = (window.parent && window.parent.getComputedStyle)
                    ? window.parent.getComputedStyle(sidebar)
                    : window.getComputedStyle(sidebar);
                const width = sidebar.offsetWidth || sidebar.clientWidth;
                const isCollapsed = width === 0 || computed.display === 'none' || computed.visibility === 'hidden';
                
                if (isCollapsed) {
                    toggleButton.classList.add('sidebar-expanded');
                } else {
                    toggleButton.classList.remove('sidebar-expanded');
                }
            };

            const ensureSidebarExpanded = () => {
                const sidebar = doc.querySelector('[data-testid="stSidebar"]');
                if (!sidebar) {
                    return;
                }
                const computed = (window.parent && window.parent.getComputedStyle)
                    ? window.parent.getComputedStyle(sidebar)
                    : window.getComputedStyle(sidebar);
                const width = sidebar.offsetWidth || sidebar.clientWidth;
                const isCollapsed = width === 0 || computed.display === 'none' || computed.visibility === 'hidden';
                if (isCollapsed) {
                    triggerSidebarToggle(true);
                }
                updateButtonState();
            };

            toggleButton.addEventListener("click", () => {
                triggerSidebarToggle(false);
                setTimeout(updateButtonState, 350);
            });
            toggleButton.addEventListener("keydown", (event) => {
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    triggerSidebarToggle(false);
                    setTimeout(updateButtonState, 350);
                }
            });

            // 监听sidebar宽度变化
            const observer = new MutationObserver(updateButtonState);
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (sidebar) {
                observer.observe(sidebar, {
                    attributes: true,
                    attributeFilter: ['style', 'class', 'aria-expanded']
                });
            }

            doc.body.appendChild(toggleButton);
            setTimeout(ensureSidebarExpanded, 60);
            setInterval(updateButtonState, 500);
        })();
        </script>
        """,
        height=0,
        width=0,
    )


mount_sidebar_toggle_button()


def sync_main_container_layout() -> None:
    components.html(
        """
        <script>
        (function() {
            const win = window.parent || window;
            if (!win) {
                return;
            }
            const doc = win.document;
            if (!doc) {
                return;
            }
            win.__HEVY_LAYOUT_STATE__ = win.__HEVY_LAYOUT_STATE__ || {};
            const state = win.__HEVY_LAYOUT_STATE__;
            const schedule = win.requestAnimationFrame || window.requestAnimationFrame || function(cb) {
                return setTimeout(cb, 16);
            };

            if (state.mainObserver && typeof state.mainObserver.disconnect === "function") {
                state.mainObserver.disconnect();
                state.mainObserver = null;
            }
            if (state.sidebarMutationObserver && typeof state.sidebarMutationObserver.disconnect === "function") {
                state.sidebarMutationObserver.disconnect();
                state.sidebarMutationObserver = null;
            }
            if (state.resizeHandler && typeof state.resizeHandler === "function") {
                win.removeEventListener("resize", state.resizeHandler);
                state.resizeHandler = null;
            }
            state.kickoffCount = 0;

            const getBlock = () => doc.querySelector('[data-testid="block-container"]') ||
                doc.querySelector('.block-container') ||
                doc.querySelector('main [data-testid="block-container"]') ||
                doc.querySelector('main .block-container');

            const updateMetrics = () => {
                const block = getBlock();
                if (!block) {
                    return;
                }
                const rect = block.getBoundingClientRect();
                doc.documentElement.style.setProperty('--hevy-main-width', `${rect.width}px`);
                doc.documentElement.style.setProperty('--hevy-main-left', `${rect.left}px`);
            };

            const initObservers = () => {
                const block = getBlock();
                if (!block) {
                    schedule(initObservers);
                    return;
                }
                const sidebar = doc.querySelector('[data-testid="stSidebar"]');
                const ResizeObserverCtor = win.ResizeObserver || window.ResizeObserver;
                const MutationObserverCtor = win.MutationObserver || window.MutationObserver;
                if (ResizeObserverCtor) {
                    const observer = new ResizeObserverCtor(() => {
                        schedule(() => updateMetrics());
                    });
                    observer.observe(block);
                    if (sidebar) {
                        observer.observe(sidebar);
                    }
                    state.mainObserver = observer;
                }
                if (sidebar && MutationObserverCtor) {
                    const mutationObserver = new MutationObserverCtor(() => {
                        schedule(() => updateMetrics());
                    });
                    mutationObserver.observe(sidebar, {
                        attributes: true,
                        attributeFilter: ["aria-expanded", "style", "class"],
                    });
                    state.sidebarMutationObserver = mutationObserver;
                }
                state.resizeHandler = () => {
                    schedule(() => updateMetrics());
                };
                win.addEventListener("resize", state.resizeHandler);
                const kickoff = () => {
                    updateMetrics();
                    state.kickoffCount = (state.kickoffCount || 0) + 1;
                    if ((state.kickoffCount || 0) < 5) {
                        schedule(kickoff);
                    }
                };
                kickoff();
            };

            initObservers();
        })();
        </script>
        """,
        height=0,
        width=0,
    )


sync_main_container_layout()

if STREAMLIT_FLOAT_READY:
    st.markdown(
        """
        <style>
        .floating-controls-panel-wrapper {
            position: static !important;
            bottom: auto !important;
            right: auto !important;
            left: auto !important;
            transform: none !important;
            width: 100%;
        }
        /* 给floated的Toolbar容器添加毛玻璃背景 */
        div:has(>.element-container div[class*="flt-"]) {
            background: rgba(255, 255, 255, 0.65) !important;
            border: 1px solid rgba(255, 255, 255, 0.35) !important;
            border-radius: 8px !important;
            padding: 0.2rem 0.3rem !important;
            backdrop-filter: blur(20px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
            box-shadow: 0 8px 32px rgba(11, 15, 24, 0.1), 0 2px 8px rgba(11, 15, 24, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
        }
        /* 压缩stVerticalBlock容器高度 */
        div:has(>.element-container div[class*="flt-"]) .stVerticalBlock {
            gap: 0.15rem !important;
            row-gap: 0.15rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <style>
    .floating-toolbar-anchor {
        display: none;
    }
    /* Toolbar整体容器 - 添加圆角背景 */
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) {
        padding: 0 !important;
        margin: 0 !important;
    }
    /* Toolbar主体 - 极度压缩高度，使用主内容区域的宽度变量确保居中对齐 */
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) > div[data-testid="stHorizontalBlock"] {
        position: relative;
        display: grid;
        grid-template-columns: minmax(120px, 140px) minmax(240px, 280px) minmax(140px, 160px);
        gap: 0.15rem;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(250, 251, 254, 0.98));
        border: 1px solid rgba(15, 23, 42, 0.12);
        border-radius: 14px;
        padding: 0.25rem 0.35rem 0.25rem 1.85rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(11, 15, 24, 0.08), 0 1px 4px rgba(11, 15, 24, 0.06);
        align-items: center;
        max-width: 650px;
        width: fit-content;
        margin: 0.5rem auto;
    }
    /* 移除外层阴影效果 */
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) > div[data-testid="stHorizontalBlock"]::before {
        display: none;
    }
    /* Column基础样式 - 消除padding */
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) > div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        position: relative;
        z-index: 1;
        padding: 0 !important;
        margin: 0 !important;
    }
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) > div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
        margin-bottom: 0 !important;
        margin-top: 0 !important;
        gap: 0 !important;
        width: 100%;
    }
    /* 带chip的column - 更紧凑 */
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) [data-testid="column"]:has(.toolbar-chip) {
        position: relative;
        display: block;
        background: rgba(247, 248, 252, 0.6);
        border-radius: 8px;
        padding: 0.12rem 0.28rem 0.06rem;
        padding-top: 0.22rem;
        border: 1px solid rgba(15, 23, 42, 0.06);
        overflow: visible;
    }
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) [data-testid="column"]:has(.toolbar-chip[data-chip="pr"]) {
        align-items: center;
    }
    /* Chip标签定位 - 更靠上 */
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) [data-testid="column"]:has(.toolbar-chip) > div[data-testid="stVerticalBlock"]:first-child {
        position: absolute;
        top: 0.35rem;
        left: 0.28rem;
        right: 0.28rem;
        display: flex;
        align-items: center;
        margin-bottom: 0;
        pointer-events: none;
    }
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) [data-testid="column"]:has(.toolbar-chip) > div[data-testid="stVerticalBlock"]:not(:first-child) {
        display: flex;
        align-items: center;
        margin-top: 0 !important;
        gap: 0 !important;
    }
    /* Shell容器 - 消除间距 */
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) .toolbar-control-shell,
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) .toolbar-period-shell,
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) .toolbar-source-shell {
        width: 100%;
        display: flex;
        align-items: center;
        gap: 0;
        margin: 0;
        padding: 0;
    }
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) .toolbar-control-shell {
        min-height: 12px;
    }
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) .toolbar-period-shell {
        justify-content: space-between;
        align-items: center;
        gap: 0.15rem;
    }
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) .toolbar-period-shell [data-testid="column"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) .toolbar-period-shell [data-testid="column"] > div[data-testid="stVerticalBlock"] {
        margin-bottom: 0 !important;
        margin-top: 0 !important;
        gap: 0 !important;
    }
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) .toolbar-source-shell {
        width: 100%;
    }
    /* Chip文字 - 更小更紧凑 */
    .toolbar-chip {
        font-size: 0.6rem;
        letter-spacing: 0.08em;
        font-weight: 700;
        color: #6b7280;
        text-transform: uppercase;
        line-height: 1;
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        min-height: 0.55rem;
        padding: 0;
        text-align: center;
        background: transparent;
        transform: translateY(-12px);
    }
    /* Selectbox样式 - 极度压缩 */
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) div[data-testid="stSelectbox"] {
        width: 100%;
        margin: 0 !important;
    }
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) div[data-testid="stSelectbox"] label {
        display: none !important;
    }
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) div[data-testid="stSelectbox"] > div {
        gap: 0 !important;
        margin: 0 !important;
    }
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        width: 100%;
        border-radius: 8px;
        border: 1px solid rgba(15, 23, 42, 0.08);
        background: #ffffff;
        min-height: 24px !important;
        max-height: 24px !important;
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.5);
    }
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) div[data-testid="stSelectbox"] [role="button"] {
        padding: 0.15rem 0.2rem 0.15rem 0.3rem !important;
        min-height: 22px !important;
        max-height: 22px !important;
        line-height: 1 !important;
    }
    /* Selectbox文字 - 更小 */
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) div[data-testid="stSelectbox"] [class*="SingleValue"] {
        font-size: 0.7rem !important;
        font-weight: 600;
        color: #1f2937 !important;
        line-height: 1 !important;
    }
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) div[data-testid="stSelectbox"] svg {
        width: 14px !important;
        height: 14px !important;
    }
    /* Period导航按钮 - 更小 */
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) .toolbar-period-shell button {
        font-size: 0.75rem;
        padding: 0.15rem 0.2rem !important;
        min-height: 24px !important;
        max-height: 24px !important;
        line-height: 1 !important;
    }
    div[data-testid="element-container"].st-key-floating_period_prev button,
    div[data-testid="element-container"].st-key-floating_period_next button {
        width: 24px !important;
        height: 24px !important;
        min-height: 24px !important;
        max-height: 24px !important;
        border-radius: 6px;
        border: 1px solid rgba(15, 23, 42, 0.08);
        background: #ffffff;
        font-weight: 600;
        font-size: 0.7rem !important;
        color: #1f2937;
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.4);
        padding: 0 !important;
        line-height: 1 !important;
    }
    div[data-testid="element-container"].st-key-floating_period_prev button p,
    div[data-testid="element-container"].st-key-floating_period_next button p {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
    }
    div[data-testid="element-container"].st-key-floating_period_prev button:disabled,
    div[data-testid="element-container"].st-key-floating_period_next button:disabled {
        opacity: 0.3;
    }

    /* Period显示文字 */
    div[data-testid="element-container"]:has(> .floating-toolbar-anchor) .toolbar-period-display {
        font-size: 0.65rem;
        font-weight: 600;
        color: #4b5563;
        width: 100%;
        line-height: 1;
    }
    /* 响应式 */
    @media (max-width: 900px) {
        div[data-testid="element-container"]:has(> .floating-toolbar-anchor) > div[data-testid="stHorizontalBlock"] {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def trigger_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()


def fuzzy_match(text: str, query: str) -> bool:
    """
    Check if all words in query appear in text (case-insensitive).
    For example, "bench smith" matches "Bench Press (Smith Machine)".
    """
    if not query:
        return True
    if not text:
        return False
    text_lower = text.lower()
    query_words = query.lower().split()
    return all(word in text_lower for word in query_words)


def clear_workouts_filter():
    """Callback to clear the workouts filter safely from a button on_click."""
    try:
        st.session_state["workouts_list_search"] = ""
    except Exception:
        # If the widget is present, assignment here may still raise on some
        # Streamlit versions; ignore and rely on rerun to pick up the cleared
        # query via other means.
        pass
    # Set flag to auto-navigate to the page containing the selected workout
    # instead of resetting to page 1
    try:
        st.session_state["workouts_navigate_to_selected"] = True
    except Exception:
        pass
    # Mark that we want a rerun; avoid calling rerun() inside the callback
    # because some Streamlit versions treat rerun inside callbacks as a no-op.
    try:
        st.session_state["workouts_force_rerun"] = True
    except Exception:
        pass


def clear_exercises_filter():
    """Callback to clear the exercises search filter safely from a button on_click."""
    try:
        st.session_state["exercises_list_search"] = ""
    except Exception:
        pass
    # Also reset Equipment and Muscle filters
    try:
        st.session_state["exercise_filter_equipment"] = "All Equipment"
    except Exception:
        pass
    try:
        st.session_state["exercise_filter_muscle"] = "All Muscles"
    except Exception:
        pass
    # Reset Custom Exercises toggle
    try:
        st.session_state["show_custom_only"] = False
    except Exception:
        pass
    # Set flag to auto-navigate to the page containing the selected exercise
    try:
        st.session_state["exercises_navigate_to_selected"] = True
    except Exception:
        pass
    # Mark that we want a rerun
    try:
        st.session_state["exercises_force_rerun"] = True
    except Exception:
        pass


def update_active_period(period_start):
    """Set the global active period and keep the floating selectbox in sync."""
    st.session_state.active_period = period_start
    # Also persist the active period per view (Week/Month) so switching views
    # can restore the last selected period for that view.
    current_view = st.session_state.get("view_mode", "Week")
    try:
        st.session_state[f"active_period_{current_view.lower()}"] = period_start
    except Exception:
        # defensive: ignore if session state key cannot be set for some reason
        pass
    select_key = "floating_period_select"
    if period_start is not None:
        # Setting the widget-backed session_state key after the widget
        # has been instantiated can raise a StreamlitAPIException.
        # Attempt to set it but ignore the specific Streamlit error
        # if it occurs (the widget will already reflect the correct value).
        try:
            st.session_state[select_key] = period_start
        except Exception as e:  # defensive: catch StreamlitAPIException
            try:
                from streamlit.errors import StreamlitAPIException

                if isinstance(e, StreamlitAPIException):
                    # widget already exists; nothing to do
                    return
            except Exception:
                # If import failed or other error, just ignore to avoid crashing UI
                return


def sync_active_period_from_widget(periods: list[pd.Timestamp | datetime | str]) -> None:
    """Align the active period with the floating selectbox value early in the run."""
    select_key = "floating_period_select"
    # Only allow syncing from the widget when the most recent toolbar action
    # is a direct select (to avoid arrow navigation being overwritten by the
    # widget's stale value). If there's no recorded toolbar action, allow
    # initial sync.
    last_action = st.session_state.get("toolbar_last_action")
    if last_action is not None and last_action[0] != "select":
        return

    widget_period = st.session_state.get(select_key)
    if widget_period in periods and widget_period != st.session_state.get("active_period"):
        update_active_period(widget_period)


LB_TO_KG = 0.45359237
KG_TO_LB = 1 / LB_TO_KG
MI_TO_KM = 1.609344
KM_TO_MI = 1 / MI_TO_KM
IN_TO_CM = 2.54
CM_TO_IN = 1 / IN_TO_CM

MUSCLE_GROUPS = ["Back", "Chest", "Core", "Shoulders", "Arms", "Legs"]

# 细肌肉 -> 六大肌群映射（根据 exercises.csv 里的 primary_muscle / other_muscles）
MUSCLE_TO_GROUP = {
    "Abdominals": "Core",
    "Obliques": "Core",  # 腹斜肌
    "Lower Back": "Back",
    "Lats": "Back",
    "Upper Back": "Back",
    "Chest": "Chest",
    "Shoulders": "Shoulders",
    "Traps": "Back",
    "Biceps": "Arms",
    "Triceps": "Arms",
    "Forearms": "Arms",
    "Quadriceps": "Legs",
    "Hamstrings": "Legs",
    "Glutes": "Legs",
    "Adductors": "Legs",
    "Abductors": "Legs",  # 外展肌
    "Calves": "Legs",
    "Neck": "Shoulders",  # 颈部归类到肩膀组
    # 以下为特殊类型，不在热力图中显示
    "Cardio": None,
    "Full Body": None,
    "Other": None,
}

# 反向：每个大肌群有哪些细肌肉（只是一个参考集合，用的时候还是以真实数据为准）
GROUP_TO_FINE = {}
for fine, big in MUSCLE_TO_GROUP.items():
    GROUP_TO_FINE.setdefault(big, []).append(fine)


# 雷达图显示顺序参考 Hevy UI
RADAR_ORDER = ["Legs", "Chest", "Shoulders", "Back", "Arms", "Core"]


def mask_api_key(key: str) -> str:
    """Return masked API key showing only the last four characters."""
    if not key:
        return ""
    trimmed = key.strip()
    if len(trimmed) <= 4:
        return trimmed
    hidden_len = max(len(trimmed) - 4, 0)
    return f"{'*' * hidden_len}{trimmed[-4:]}"


def format_compact_number(value: float, decimals: int = 0) -> str:
    """Format large numbers with K/M suffix while keeping plain thousands.
    
    Args:
        value: The number to format
        decimals: Number of decimal places for values < 1000 (default 0)
    """
    abs_value = abs(value)
    if abs_value >= 1_000_000:
        base = value / 1_000_000
        suffix = "M"
    elif abs_value >= 1_000:
        base = value / 1_000
        suffix = "K"
    else:
        base = value
        suffix = ""

    if suffix:
        base_str = f"{base:.1f}".rstrip("0").rstrip(".")
        return f"{base_str}{suffix}"
    
    if decimals > 0:
        return f"{base:.{decimals}f}"
    return f"{base:,.0f}"


def format_metric_abs_change(metric_key: str, diff: float) -> str:
    """Return a signed, human-readable absolute delta for summary metrics."""
    if diff == 0 or diff is None:
        return "0"

    sign = "+" if diff > 0 else "-"
    abs_diff = abs(diff)

    if metric_key == "duration_hours":
        minutes_total = int(round(abs_diff * 60))
        hours = minutes_total // 60
        mins = minutes_total % 60
        if hours and mins:
            return f"{sign}{hours}h {mins:02d}m"
        if hours:
            return f"{sign}{hours}h"
        return f"{sign}{mins}m"

    if metric_key == "volume":
        converted = convert_volume_for_display(abs_diff)
        value = format_compact_number(converted)
        return f"{sign}{value} {get_weight_unit_suffix()}"

    if metric_key == "sets":
        value = f"{abs_diff:.1f}".rstrip("0").rstrip(".")
        return f"{sign}{value} Sets"

    # Default: workouts (Times)
    value = f"{int(round(abs_diff)):,}"
    return f"{sign}{value} Times"


def describe_period_range(period_start: pd.Timestamp, view_mode: str) -> str:
    """Return a human readable label for the active period window."""
    start_ts = pd.Timestamp(period_start)
    if view_mode == "Week":
        end_ts = start_ts + pd.Timedelta(days=6)
        return f"{start_ts.strftime('%b %d, %Y')} -> {end_ts.strftime('%b %d, %Y')}"
    else:
        # Month: show as "December 2024"
        return start_ts.strftime('%B %Y')


def render_segmented_buttons(
    options: list[str],
    active_value: str,
    key_prefix: str,
    columns_per_row: int | None = None,
) -> str:
    """Render pill-like buttons and return the newly selected value."""
    selected = active_value
    cols_per_row = columns_per_row or len(options)
    for start in range(0, len(options), cols_per_row):
        row = options[start : start + cols_per_row]
        columns = st.columns(len(row))
        for option, column in zip(row, columns):
            with column:
                is_active = option == selected
                if st.button(
                    option,
                    key=f"{key_prefix}_{option}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    selected = option
    return selected


def build_fetch_overlay(progress_lines: list[str]) -> str:
    """Compose the HTML for the full-screen fetch overlay including progress logs."""
    logs_html = "".join(
        f"<div class='log-line'><strong>Step {idx + 1}:</strong> {line}</div>"
        for idx, line in enumerate(progress_lines)
    )
    return (
        "<div class=\"fetch-overlay\">"
        "<div class=\"spinner\"></div>"
        "<div>Fetching workouts from Hevy...</div>"
        "<div style=\"font-size:0.85rem; font-weight:400; color: rgba(245,246,250,0.75);\">Hang tight—this might take a few seconds.</div>"
        f"<div style=\"margin-top:0.75rem; text-align:center;\">{logs_html}</div>"
        "</div>"
    )


# -----------------------------------
# 数据加载
# -----------------------------------

def load_exercises(path: str = None) -> pd.DataFrame:
    """
    内置动作表：exercises.csv
    必须至少包含列：
      - exercise_title
      - primary_muscle
      - other_muscles (可空，分号分隔)
      - media_url (可选，动作演示视频/图片链接)
    
    注意：每次调用都会重新加载文件，确保获取最新数据
    """
    if path is None:
        path = APP_DIR / "exercises.csv"
    df = pd.read_csv(path)
    # 去除关键文本字段的首尾空格，避免合并失败
    df["exercise_title"] = df["exercise_title"].astype(str).str.strip()

    # 确保必要的列存在，如果不存在则填充空值
    if "other_muscles" not in df.columns:
        df["other_muscles"] = ""
    if "media_url" not in df.columns:
        df["media_url"] = ""
    if "equipment" not in df.columns:
        df["equipment"] = ""
    
    # 填充空值
    df["primary_muscle"] = df["primary_muscle"].fillna("")
    df["other_muscles"] = df["other_muscles"].fillna("")
    df["media_url"] = df["media_url"].fillna("")
    df["equipment"] = df["equipment"].fillna("")

    # unit 列可能叫 unit，也可能从旧格式的 weight_modifier 转换而来
    # 新格式使用 unit 列（如 " KG", " LB"）
    if "unit" in df.columns:
        df["weight_modifier"] = df["unit"].fillna("")
    elif "weight_modifier" not in df.columns:
        df["weight_modifier"] = ""

    # primary -> 六大肌群
    df["primary_group"] = df["primary_muscle"].map(MUSCLE_TO_GROUP)

    # 把 other_muscles 映射成 secondary_groups（已经归类成 Back/Chest/...）
    def build_secondary_groups(row):
        s = row.get("other_muscles", np.nan)
        if pd.isna(s) or s == "":
            return ""
        groups = []
        for m in str(s).split(";"):
            m = m.strip()
            g = MUSCLE_TO_GROUP.get(m)
            if g and g != row["primary_group"]:
                if g not in groups:
                    groups.append(g)
        return ";".join(groups)

    df["secondary_groups"] = df.apply(build_secondary_groups, axis=1)

    # 合并 custom_exercises.csv 的数据（覆盖或新增）
    # custom_exercises.csv 使用 secondary_muscles 列，需要映射到 other_muscles
    if CUSTOM_EXERCISES_PATH.exists():
        try:
            custom_df = pd.read_csv(CUSTOM_EXERCISES_PATH, keep_default_na=False, na_values=[""])
            if not custom_df.empty and "exercise_title" in custom_df.columns:
                custom_df["exercise_title"] = custom_df["exercise_title"].astype(str).str.strip()
                
                # 确保必要的列存在
                if "primary_muscle" not in custom_df.columns:
                    custom_df["primary_muscle"] = ""
                if "secondary_muscles" not in custom_df.columns:
                    custom_df["secondary_muscles"] = ""
                if "equipment" not in custom_df.columns:
                    custom_df["equipment"] = ""
                
                # 映射 secondary_muscles -> other_muscles
                custom_df["other_muscles"] = custom_df["secondary_muscles"].fillna("")
                custom_df["primary_muscle"] = custom_df["primary_muscle"].fillna("")
                custom_df["equipment"] = custom_df["equipment"].fillna("")
                
                # 计算 primary_group 和 secondary_groups
                custom_df["primary_group"] = custom_df["primary_muscle"].map(MUSCLE_TO_GROUP)
                custom_df["secondary_groups"] = custom_df.apply(build_secondary_groups, axis=1)
                
                # 填充其他必要的列
                custom_df["exercise_type"] = ""
                custom_df["format"] = ""
                custom_df["weight_modifier"] = ""
                custom_df["media_url"] = ""
                
                # 对于已存在于 exercises.csv 的动作，更新其肌肉信息
                # 对于不存在的动作，添加到列表中
                for _, custom_row in custom_df.iterrows():
                    title = custom_row["exercise_title"]
                    mask = df["exercise_title"] == title
                    if mask.any():
                        # 更新已存在动作的肌肉信息
                        df.loc[mask, "primary_muscle"] = custom_row["primary_muscle"]
                        df.loc[mask, "other_muscles"] = custom_row["other_muscles"]
                        df.loc[mask, "primary_group"] = custom_row["primary_group"]
                        df.loc[mask, "secondary_groups"] = custom_row["secondary_groups"]
                        if custom_row["equipment"]:
                            df.loc[mask, "equipment"] = custom_row["equipment"]
                    else:
                        # 添加新动作
                        new_row = pd.DataFrame([{
                            "exercise_title": title,
                            "primary_muscle": custom_row["primary_muscle"],
                            "other_muscles": custom_row["other_muscles"],
                            "primary_group": custom_row["primary_group"],
                            "secondary_groups": custom_row["secondary_groups"],
                            "equipment": custom_row["equipment"],
                            "exercise_type": "",
                            "format": "",
                            "weight_modifier": "",
                            "media_url": "",
                        }])
                        df = pd.concat([df, new_row], ignore_index=True)
        except Exception:
            pass  # 如果读取失败，继续使用原有数据

    # 返回时保留细肌肉 + 大肌群两套信息，以及 media_url 和 equipment
    return df[[
        "exercise_title",
        "primary_muscle",
        "other_muscles",
        "primary_group",
        "secondary_groups",
        "equipment",
        "exercise_type",
        "format",
        "weight_modifier",
        "media_url",
    ]]


def normalize_measurement_units(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, dict[str, str]]]:
    """Normalize weight/distance columns to metric units while keeping raw columns untouched."""
    df = df.copy()
    measurement_info: dict[str, dict[str, str]] = {}
    lower_map = {col.lower(): col for col in df.columns}

    def find_column(options: list[str]) -> str | None:
        for option in options:
            if option.lower() in lower_map:
                return lower_map[option.lower()]
        return None

    # Weight per-set value
    weight_info = {"raw_column": None, "raw_unit": None, "normalized_unit": "kg"}
    weight_col = find_column(["weight_kg", "weightkg", "weight (kg)", "weight"])
    if weight_col:
        weight_info.update({"raw_column": weight_col, "raw_unit": "kg"})
        df["weight_kg"] = pd.to_numeric(df[weight_col], errors="coerce")
    else:
        weight_lb_col = find_column(["weight_lbs", "weight_lb", "weight (lbs)", "weight_pounds"])
        if weight_lb_col:
            df["weight_kg"] = pd.to_numeric(df[weight_lb_col], errors="coerce") * LB_TO_KG
            weight_info.update({"raw_column": weight_lb_col, "raw_unit": "lb"})
    if "weight_kg" not in df.columns:
        df["weight_kg"] = np.nan
    measurement_info["weight"] = weight_info

    # Body weight tracking (used for assisted/weighted movements)
    body_weight_info = {"raw_column": None, "raw_unit": None, "normalized_unit": "kg"}
    body_col = find_column(["body_weight", "bodyweight", "user_body_weight"])
    if body_col:
        body_weight_info.update({"raw_column": body_col, "raw_unit": "kg"})
        df["body_weight"] = pd.to_numeric(df[body_col], errors="coerce")
    else:
        body_lb_col = find_column(["body_weight_lbs", "bodyweight_lbs", "user_body_weight_lbs"])
        if body_lb_col:
            df["body_weight"] = pd.to_numeric(df[body_lb_col], errors="coerce") * LB_TO_KG
            body_weight_info.update({"raw_column": body_lb_col, "raw_unit": "lb"})
    measurement_info["body_weight"] = body_weight_info

    # Distance tracking (e.g., running rows)
    distance_info = {"raw_column": None, "raw_unit": None, "normalized_unit": "km"}
    distance_km_col = find_column(["distance_km", "distance_kilometers"])
    if distance_km_col:
        df["distance_km"] = pd.to_numeric(df[distance_km_col], errors="coerce")
        distance_info.update({"raw_column": distance_km_col, "raw_unit": "km"})
    else:
        distance_miles_col = find_column(["distance_miles", "distance_mi"])
        if distance_miles_col:
            df["distance_km"] = pd.to_numeric(df[distance_miles_col], errors="coerce") * MI_TO_KM
            distance_info.update({"raw_column": distance_miles_col, "raw_unit": "mi"})
    if distance_info["raw_column"]:
        measurement_info["distance"] = distance_info

    # Range of motion (less common, but keep parity with Hevy exports)
    rom_info = {"raw_column": None, "raw_unit": None, "normalized_unit": "cm"}
    rom_cm_col = find_column(["range_of_motion_cm"])
    if rom_cm_col:
        df["range_of_motion_cm"] = pd.to_numeric(df[rom_cm_col], errors="coerce")
        rom_info.update({"raw_column": rom_cm_col, "raw_unit": "cm"})
    else:
        rom_in_col = find_column(["range_of_motion_in", "range_of_motion_inches"])
        if rom_in_col:
            df["range_of_motion_cm"] = pd.to_numeric(df[rom_in_col], errors="coerce") * IN_TO_CM
            rom_info.update({"raw_column": rom_in_col, "raw_unit": "in"})
    if rom_info["raw_column"]:
        measurement_info["range_of_motion"] = rom_info

    return df, measurement_info


def get_weight_display_unit() -> str:
    return st.session_state.get("weight_unit_preference", "kg")


def get_distance_display_unit() -> str:
    return st.session_state.get("distance_unit_preference", "kilometers")


def get_weight_unit_suffix() -> str:
    return "KG" if get_weight_display_unit() == "kg" else "LBS"


def get_distance_unit_suffix() -> str:
    return "KM" if get_distance_display_unit() == "kilometers" else "MI"


def convert_weight_for_display(value_kg: float | pd.Series) -> float | pd.Series:
    if value_kg is None:
        return 0.0
    if get_weight_display_unit() == "kg":
        return value_kg
    return value_kg * KG_TO_LB


def convert_volume_for_display(value_kg: float | pd.Series) -> float | pd.Series:
    # Volume has same unit dimension as weight
    return convert_weight_for_display(value_kg)


def convert_distance_for_display(value_km: float | pd.Series) -> float | pd.Series:
    if value_km is None:
        return 0.0
    if get_distance_display_unit() == "kilometers":
        return value_km
    return value_km * KM_TO_MI


API_KEY_STORE_PATH = APP_DIR / ".remembered_api_key.json"
USER_PREFS_PATH = APP_DIR / ".user_preferences.json"
CUSTOM_EXERCISES_PATH = APP_DIR / "custom_exercises.csv"


def load_custom_exercises() -> pd.DataFrame:
    """Load custom exercises from CSV file."""
    if not CUSTOM_EXERCISES_PATH.exists():
        return pd.DataFrame(columns=["exercise_title", "equipment", "primary_muscle", "secondary_muscles"])
    try:
        df = pd.read_csv(CUSTOM_EXERCISES_PATH, keep_default_na=False, na_values=[""])
        # Ensure required columns exist
        for col in ["exercise_title", "equipment", "primary_muscle", "secondary_muscles"]:
            if col not in df.columns:
                df[col] = ""
        df = df.fillna("")
        return df
    except Exception:
        return pd.DataFrame(columns=["exercise_title", "equipment", "primary_muscle", "secondary_muscles"])


def save_custom_exercise(exercise_title: str, equipment: str, primary_muscle: str, secondary_muscles: str) -> None:
    """Save or update a custom exercise to CSV file."""
    df = load_custom_exercises()
    # Check if exercise already exists
    if exercise_title in df["exercise_title"].values:
        # Update existing entry
        df.loc[df["exercise_title"] == exercise_title, "equipment"] = equipment
        df.loc[df["exercise_title"] == exercise_title, "primary_muscle"] = primary_muscle
        df.loc[df["exercise_title"] == exercise_title, "secondary_muscles"] = secondary_muscles
    else:
        # Add new entry
        new_row = pd.DataFrame([{
            "exercise_title": exercise_title,
            "equipment": equipment,
            "primary_muscle": primary_muscle,
            "secondary_muscles": secondary_muscles,
        }])
        df = pd.concat([df, new_row], ignore_index=True)
    # Save to CSV
    try:
        df.to_csv(CUSTOM_EXERCISES_PATH, index=False)
    except Exception:
        pass


def get_custom_exercise_metadata(exercise_title: str) -> dict:
    """Get metadata for a custom exercise from saved file."""
    df = load_custom_exercises()
    if exercise_title in df["exercise_title"].values:
        row = df[df["exercise_title"] == exercise_title].iloc[0]
        return {
            "equipment": row.get("equipment", "") or "",
            "primary_muscle": row.get("primary_muscle", "") or "",
            "secondary_muscles": row.get("secondary_muscles", "") or "",
        }
    return {"equipment": "", "primary_muscle": "", "secondary_muscles": ""}


def get_custom_exercises_csv_bytes() -> bytes:
    """Get custom exercises CSV as bytes for download."""
    df = load_custom_exercises()
    if df.empty:
        # Return template
        df = pd.DataFrame(columns=["exercise_title", "equipment", "primary_muscle", "secondary_muscles"])
    return df.to_csv(index=False).encode("utf-8")


def get_unconfigured_custom_exercises(raw_hevy_df: pd.DataFrame) -> list:
    """
    Find exercises in user's workout data that are not in exercises.csv 
    and not yet configured in custom_exercises.csv (i.e., have no primary_muscle set).
    Returns a list of exercise titles that need configuration.
    """
    if raw_hevy_df is None or raw_hevy_df.empty:
        return []
    
    try:
        # Load exercises.csv
        exercises_csv = pd.read_csv(APP_DIR / "exercises.csv", keep_default_na=False, na_values=[""])
        csv_exercise_titles = set(exercises_csv["exercise_title"].astype(str).str.strip().unique())
    except Exception:
        csv_exercise_titles = set()
    
    # Load custom_exercises.csv
    custom_ex_df = load_custom_exercises()
    # Only consider configured if primary_muscle is set
    if not custom_ex_df.empty and "primary_muscle" in custom_ex_df.columns:
        configured_custom = set(
            custom_ex_df[custom_ex_df["primary_muscle"].fillna("").str.strip() != ""]["exercise_title"].unique()
        )
    else:
        configured_custom = set()
    
    # Find user's exercises
    user_exercise_titles = set(raw_hevy_df["exercise_title"].astype(str).str.strip().unique())
    
    # Unconfigured = in user data, not in exercises.csv, and not configured in custom_exercises.csv
    unconfigured = user_exercise_titles - csv_exercise_titles - configured_custom
    return sorted(list(unconfigured))


def load_persisted_api_key() -> str:
    if not API_KEY_STORE_PATH.exists():
        return ""
    try:
        payload = json.loads(API_KEY_STORE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    return str(payload.get("api_key", ""))


def persist_api_key_value(api_key: str) -> None:
    if not api_key:
        return
    try:
        API_KEY_STORE_PATH.write_text(json.dumps({"api_key": api_key}), encoding="utf-8")
    except OSError:
        pass


def clear_persisted_api_key() -> None:
    try:
        API_KEY_STORE_PATH.unlink(missing_ok=True)
    except OSError:
        pass


def sync_persisted_api_key(api_key: str, remember: bool) -> None:
    if remember and api_key:
        persist_api_key_value(api_key)
    else:
        clear_persisted_api_key()


def clear_saved_api_key_state(clear_pending: bool = True):
    st.session_state["remember_api_key"] = False
    st.session_state["api_key_value"] = ""
    if clear_pending:
        st.session_state["pending_api_key"] = ""
    sync_persisted_api_key("", False)


def load_user_preferences() -> dict:
    if not USER_PREFS_PATH.exists():
        return {}
    try:
        return json.loads(USER_PREFS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def update_user_preferences(**kwargs) -> None:
    prefs = load_user_preferences()
    changed = False
    for key, value in kwargs.items():
        if value is None:
            continue
        if prefs.get(key) != value:
            prefs[key] = value
            changed = True
    if not changed:
        return
    try:
        USER_PREFS_PATH.write_text(json.dumps(prefs, indent=2), encoding="utf-8")
    except OSError:
        pass


@st.cache_data
def load_hevy_workouts(file) -> pd.DataFrame:
    """
    用户上传的 hevy_workouts.csv
    必须至少包含列：
      - title
      - start_time
      - end_time
      - exercise_title
      - set_type
      - weight_kg
      - reps
    """
    # Try multiple encodings to handle different file sources
    encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'gbk', 'gb2312']
    
    for encoding in encodings_to_try:
        try:
            # Reset file position if it's a file-like object
            if hasattr(file, 'seek'):
                file.seek(0)
            df = pd.read_csv(file, encoding=encoding)
            return df
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    # If all encodings fail, try with error handling
    if hasattr(file, 'seek'):
        file.seek(0)
    df = pd.read_csv(file, encoding='utf-8', errors='replace')
    return df


# -----------------------------------
# 预处理 & 派生字段
# -----------------------------------

def attach_muscle_groups(workouts: pd.DataFrame, exercises: pd.DataFrame) -> pd.DataFrame:
    """把 exercises.csv 里的肌肉信息（细肌肉+大肌群）贴到每组 set 上。"""
    merged = workouts.merge(exercises, on="exercise_title", how="left")
    return merged


def prepare_workout_df(raw_df: pd.DataFrame, ex_df: pd.DataFrame) -> pd.DataFrame:
    """
    从 hevy_workouts.csv + exercises.csv 构造统一的 set 级别 DataFrame。
    """
    df = raw_df.copy()

    # 标准化关键文本字段，避免因为前后空格导致合并不到肌群/动作信息
    df["exercise_title"] = df["exercise_title"].astype(str).str.strip()

    # 解析时间
    # Parse timestamps from both API (ISO8601) and CSV exports (day-first)
    df["start_dt"] = pd.to_datetime(df["start_time"], format="ISO8601", errors="coerce")
    df["end_dt"] = pd.to_datetime(df["end_time"], format="ISO8601", errors="coerce")
    start_missing = df["start_dt"].isna() & df["start_time"].notna()
    end_missing = df["end_dt"].isna() & df["end_time"].notna()
    if start_missing.any():
        df.loc[start_missing, "start_dt"] = pd.to_datetime(
            df.loc[start_missing, "start_time"], errors="coerce", dayfirst=True
        )
    if end_missing.any():
        df.loc[end_missing, "end_dt"] = pd.to_datetime(
            df.loc[end_missing, "end_time"], errors="coerce", dayfirst=True
        )
    df["date"] = df["start_dt"].dt.date

    # 构造 workout_id（title + start_time）
    df["workout_id"] = df["title"].astype(str) + " | " + df["start_dt"].astype(str)

    # 重命名 weight / 处理 reps
    df["weight"] = pd.to_numeric(df["weight_kg"], errors="coerce").fillna(0.0)
    df["reps"] = pd.to_numeric(df["reps"], errors="coerce").fillna(0).astype(int)
    if "set_index" in df.columns:
        df["set_index"] = pd.to_numeric(df["set_index"], errors="coerce")

    # set_type 统一小写
    df["set_type"] = df["set_type"].fillna("").str.lower()

    # 贴肌群信息（会得到 primary_muscle / other_muscles / primary_group / secondary_groups / format）
    df = attach_muscle_groups(df, ex_df)
    
    # 确保body_weight列存在（CSV上传的数据可能没有这个字段）
    if "body_weight" not in df.columns:
        df["body_weight"] = None

    # 计算每个 workout 的时长（分钟）
    workout_duration = (
        df.groupby("workout_id")["end_dt"].first()
        - df.groupby("workout_id")["start_dt"].first()
    )
    workout_duration_min = workout_duration.dt.total_seconds() / 60.0
    df = df.merge(
        workout_duration_min.rename("workout_duration_min"),
        on="workout_id",
        how="left",
    )

    return df


def get_set_effective_factor(set_type: str, drop_set_factor: float = None) -> float:
    """
    warmup: 0
    normal: 1.0
    dropset / myo: configurable (default 0.5)
    其他：按 1.0 处理
    """
    s = (set_type or "").lower()
    if "warm" in s:
        return 0.0
    if "drop" in s or "myo" in s:
        # Use provided factor or get from session state
        if drop_set_factor is None:
            drop_set_factor = st.session_state.get("drop_set_factor", 0.5)
        return float(drop_set_factor)
    return 1.0


def add_effective_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """增加 effective_set_factor + set_volume。
    对于-KG和+KG类型的exercises，调整weight计算：
    - ' -KG' (Assisted): effective_weight = body_weight - recorded_weight
    - ' +KG' (Weighted): effective_weight = body_weight + recorded_weight
    """
    df = df.copy()
    df["effective_set_factor"] = df["set_type"].apply(get_set_effective_factor)
    
    # 获取exercise_type信息（从exercises.csv已经merge过来）
    # exercise_type字段格式如：'Assisted Bodyweight', 'Weighted Bodyweight', 'Weight & Reps' 等
    df["exercise_type"] = df.get("exercise_type", pd.Series([""] * len(df))).fillna("")
    df["body_weight"] = pd.to_numeric(df.get("body_weight", pd.Series([None] * len(df))), errors="coerce")
    
    # 计算adjusted weight
    def calculate_adjusted_weight(row):
        weight = row["weight"]
        exercise_type = str(row.get("exercise_type", "")).lower()
        body_weight = row.get("body_weight")
        
        # 根据 exercise_type 判断是否是 Assisted/Weighted Bodyweight
        is_assisted_bw = "assisted" in exercise_type and "bodyweight" in exercise_type
        is_weighted_bw = "weighted" in exercise_type and "bodyweight" in exercise_type
        
        # Check if bodyweight inclusion is enabled
        include_bodyweight = True
        try:
            include_bodyweight = bool(st.session_state.get("include_bodyweight", True))
        except Exception:
            include_bodyweight = True
        
        if is_assisted_bw and body_weight is not None and include_bodyweight:
            # Assisted Bodyweight: body_weight - assistance_weight
            try:
                return float(body_weight) - weight
            except (ValueError, TypeError):
                return weight
        elif is_weighted_bw and body_weight is not None and include_bodyweight:
            # Weighted Bodyweight: body_weight + additional_weight
            try:
                return float(body_weight) + weight
            except (ValueError, TypeError):
                return weight
        else:
            # 普通weight (or bodyweight inclusion disabled)
            return weight
    
    df["adjusted_weight"] = df.apply(calculate_adjusted_weight, axis=1)
    df["set_volume"] = df["adjusted_weight"] * df["reps"]
    # Compute metric-aware columns that respect the global setting whether to include warmup sets
    include_warmups = False
    try:
        include_warmups = bool(st.session_state.get("include_warmup_sets", False))
    except Exception:
        include_warmups = False

    # metric_set_volume: set_volume included only when warming-up inclusion is enabled
    if include_warmups:
        df["metric_set_volume"] = df["set_volume"].fillna(0.0)
    else:
        df["metric_set_volume"] = df["set_volume"].where(~df["set_type"].str.contains("warm", na=False), 0.0).fillna(0.0)

    # metric_set_factor: effective_set_factor adjusted to count warmups as 1.0 when enabled
    if include_warmups:
        df["metric_set_factor"] = df["effective_set_factor"].copy()
        try:
            df.loc[df["set_type"].str.contains("warm", na=False), "metric_set_factor"] = 1.0
        except Exception:
            pass
    else:
        df["metric_set_factor"] = df["effective_set_factor"].fillna(0.0)
    
    return df


def add_period_columns(df: pd.DataFrame, week_start: str = "Monday") -> pd.DataFrame:
    """增加 week_period / month_period。
    week_start: "Monday" 或 "Sunday"
    """
    df = df.copy()
    date_series = pd.to_datetime(df["date"], errors="coerce")
    # W-SUN: week ends on Sunday (Mon-Sun), W-SAT: week ends on Saturday (Sun-Sat)
    week_anchor = "W-SUN" if week_start == "Monday" else "W-SAT"
    df["week_period"] = date_series.dt.to_period(week_anchor).apply(
        lambda r: r.start_time.date() if pd.notna(r) else None
    )
    df["month_period"] = date_series.dt.to_period("M").apply(
        lambda r: r.start_time.date() if pd.notna(r) else None
    )
    return df


# -----------------------------------
# 聚合：周期 Summary
# -----------------------------------

def build_period_summary(df: pd.DataFrame, view_mode: str, week_start: str = "Monday") -> pd.DataFrame:
    """
    返回：
      period_start | workouts | duration_hours | volume | sets
    
    对于 Week 模式：返回过去 16 周的汇总（包括无数据的周）
    对于 Month 模式：返回过去 12 个月的汇总（包括无数据的月）
    week_start: "Monday" 或 "Sunday"
    """
    # 根据week_start重新计算week_period
    if view_mode == "Week":
        date_series = pd.to_datetime(df["date"], errors="coerce")
        week_anchor = "W-SUN" if week_start == "Monday" else "W-SAT"
        df = df.copy()
        df["week_period"] = date_series.dt.to_period(week_anchor).apply(
            lambda r: r.start_time.date() if pd.notna(r) else None
        )
    
    period_col = "week_period" if view_mode == "Week" else "month_period"

    # 生成完整的周期范围
    if view_mode == "Week":
        # 获取最新的周期日期，如果没有数据则用今天
        # Filter out None/NaN values before getting max
        valid_periods = df[period_col].dropna() if period_col in df.columns else pd.Series(dtype=object)
        if len(valid_periods) > 0:
            max_date = max(valid_periods)
        else:
            # 使用今天周一作为基准
            today = pd.Timestamp.now().date()
            max_date = today - pd.Timedelta(days=today.weekday())  # 上周一
        
        # 生成过去 16 周的范围（从最新周往回）
        periods_list = []
        for i in range(16):
            period_date = max_date - pd.Timedelta(weeks=i)
            periods_list.append(period_date)
        periods_list = sorted(periods_list)
    else:  # Month
        # 获取最新的月份日期，如果没有数据则用本月
        # Filter out None/NaN values before getting max
        valid_periods = df[period_col].dropna() if period_col in df.columns else pd.Series(dtype=object)
        if len(valid_periods) > 0:
            max_date = max(valid_periods)
        else:
            max_date = pd.Timestamp.now().date().replace(day=1)
        
        # 生成过去 12 个月的范围（从最新月往回）
        periods_list = []
        current = max_date
        for i in range(12):
            periods_list.append(current)
            # 往前推一个月
            if current.month == 1:
                current = current.replace(year=current.year - 1, month=12)
            else:
                current = current.replace(month=current.month - 1)
        periods_list = sorted(periods_list)

    # 对现有数据进行聚合
    if not df.empty and period_col in df.columns:
        # 为了正确计算duration，先按workout_id去重，再按period聚合
        workout_durations = df.groupby(["workout_id", period_col])["workout_duration_min"].first().reset_index()
        
        agg = (
            df.groupby(period_col)
            .agg(
                workouts=("workout_id", "nunique"),
                volume=("metric_set_volume", "sum"),
                sets=("metric_set_factor", "sum"),
            )
            .reset_index()
            .rename(columns={period_col: "period_start"})
        )
        
        # 单独计算duration
        duration_agg = (
            workout_durations.groupby(period_col)["workout_duration_min"]
            .sum()
            .reset_index()
        )
        duration_agg["duration_hours"] = duration_agg["workout_duration_min"] / 60.0
        duration_agg = duration_agg[[period_col, "duration_hours"]].rename(columns={period_col: "period_start"})
        
        # 合并duration到主结果
        agg = agg.merge(duration_agg, on="period_start", how="left")
        agg["duration_hours"] = agg["duration_hours"].fillna(0)
    else:
        agg = pd.DataFrame(columns=["period_start", "workouts", "duration_hours", "volume", "sets"])

    # 创建完整的周期范围 DataFrame（包括无数据的周期）
    full_periods = pd.DataFrame({"period_start": periods_list})
    
    # 左连接，确保所有周期都包含（无数据的用 0 填充）
    result = full_periods.merge(agg, on="period_start", how="left")
    result = result.fillna(0)

    return result.sort_values("period_start")


# -----------------------------------
# 聚合：Muscle Distribution（大肌群）
# -----------------------------------

def build_muscle_distribution(df: pd.DataFrame, view_mode: str, metric: str, week_start: str = "Monday") -> pd.DataFrame:
    """
    返回：period_start | muscle_group | value
    metric ∈ ["Workouts", "Duration", "Volume", "Sets"]
    week_start: "Monday" 或 "Sunday"
    """
    # 根据week_start重新计算week_period
    if view_mode == "Week":
        date_series = pd.to_datetime(df["date"], errors="coerce")
        week_anchor = "W-SUN" if week_start == "Monday" else "W-SAT"
        df = df.copy()
        df["week_period"] = date_series.dt.to_period(week_anchor).apply(
            lambda r: r.start_time.date() if pd.notna(r) else None
        )
    
    period_col = "week_period" if view_mode == "Week" else "month_period"
    
    # Get secondary muscle factor from session state
    secondary_factor = 0.5
    try:
        secondary_factor = float(st.session_state.get("secondary_muscle_factor", 0.5))
    except Exception:
        secondary_factor = 0.5

    rows = []
    for _, row in df.iterrows():
        period = row[period_col]
        wid = row["workout_id"]
        factor = row.get("metric_set_factor", row.get("effective_set_factor", 0.0))
        vol = row.get("metric_set_volume", row.get("set_volume", 0.0))

        # primary：权重 1.0
        pg = row.get("primary_group", None)
        if isinstance(pg, str) and pg in MUSCLE_GROUPS:
            rows.append(
                {
                    "period": period,
                    "workout_id": wid,
                    "muscle_group": pg,
                    "set_factor": factor * 1.0,
                    "volume": vol * 1.0,
                }
            )

        # secondary：secondary_groups 字符串拆分，权重从设置获取
        sg_str = row.get("secondary_groups", "") or ""
        if isinstance(sg_str, str) and sg_str.strip():
            for m in sg_str.split(";"):
                m = m.strip()
                if m and m in MUSCLE_GROUPS:
                    rows.append(
                        {
                            "period": period,
                            "workout_id": wid,
                            "muscle_group": m,
                            "set_factor": factor * secondary_factor,
                            "volume": vol * secondary_factor,
                        }
                    )

    if not rows:
        return pd.DataFrame(columns=["period_start", "muscle_group", "value"])

    mdf = pd.DataFrame(rows)

    # 贴回 workout_duration_min，用于 Duration 计算
    wd = df.groupby("workout_id")["workout_duration_min"].first()
    mdf = mdf.merge(wd.rename("workout_duration_min"), on="workout_id", how="left")

    if metric == "Workouts":
        # 先按 workout_id 和 muscle_group 去重（同一个 workout 的多个细分肌肉只算一次大肌肉群）
        unique_workouts = mdf[["period", "workout_id", "muscle_group"]].drop_duplicates()
        grouped = unique_workouts.groupby(["period", "muscle_group"])["workout_id"].nunique()
    elif metric == "Duration":
        muscle_count = mdf.groupby(["period", "workout_id"])["muscle_group"].nunique()
        mdf = mdf.join(muscle_count.rename("muscle_count"), on=["period", "workout_id"])
        mdf["duration_hours_share"] = (
            mdf["workout_duration_min"] / mdf["muscle_count"] / 60.0
        )
        grouped = mdf.groupby(["period", "muscle_group"])["duration_hours_share"].sum()
    elif metric == "Volume":
        grouped = mdf.groupby(["period", "muscle_group"])["volume"].sum()
    else:  # Sets
        grouped = mdf.groupby(["period", "muscle_group"])["set_factor"].sum()

    res = grouped.reset_index().rename(columns={"period": "period_start"})
    if "value" in res.columns:
        pass
    else:
        # 最后一列就是 value
        val_col = [c for c in res.columns if c not in ["period_start", "muscle_group"]][0]
        res = res.rename(columns={val_col: "value"})
    return res


# -----------------------------------
# 新增：细肌肉分布（Biceps / Triceps / …）
# -----------------------------------

def build_detailed_muscle_distribution(df: pd.DataFrame, view_mode: str, metric: str, week_start: str = "Monday") -> pd.DataFrame:
    """
    返回：period_start | big_group | fine_muscle | value
    metric ∈ ["Workouts", "Duration", "Volume", "Sets"]
    week_start: "Monday" 或 "Sunday"
    """
    # 根据week_start重新计算week_period（与build_muscle_distribution保持一致）
    if view_mode == "Week":
        date_series = pd.to_datetime(df["date"], errors="coerce")
        week_anchor = "W-SUN" if week_start == "Monday" else "W-SAT"
        df = df.copy()
        df["week_period"] = date_series.dt.to_period(week_anchor).apply(
            lambda r: r.start_time.date() if pd.notna(r) else None
        )
    
    period_col = "week_period" if view_mode == "Week" else "month_period"
    
    # Get secondary muscle factor from session state
    secondary_factor = 0.5
    try:
        secondary_factor = float(st.session_state.get("secondary_muscle_factor", 0.5))
    except Exception:
        secondary_factor = 0.5

    # 定义肌肉组包含关系（单向映射）
    # Traps 包含 Upper Back 的数据（Upper Back 动作也计入 Traps）
    # 但 Upper Back 不包含 Traps 的数据
    MUSCLE_INCLUDES = {
        "Upper Back": ["Traps"],  # Upper Back 的数据也计入 Traps
    }

    rows = []
    for _, row in df.iterrows():
        period = row[period_col]
        wid = row["workout_id"]
        factor = row.get("metric_set_factor", row.get("effective_set_factor", 0.0))
        vol = row.get("metric_set_volume", row.get("set_volume", 0.0))

        # primary 细肌肉
        pm = row.get("primary_muscle", None)
        if isinstance(pm, str) and pm in MUSCLE_TO_GROUP:
            big = MUSCLE_TO_GROUP[pm]
            rows.append(
                {
                    "period": period,
                    "workout_id": wid,
                    "big_group": big,
                    "fine_muscle": pm,
                    "set_factor": factor * 1.0,
                    "volume": vol * 1.0,
                }
            )
            # 如果该肌肉的数据需要计入其他肌肉
            if pm in MUSCLE_INCLUDES:
                for target_muscle in MUSCLE_INCLUDES[pm]:
                    target_big = MUSCLE_TO_GROUP.get(target_muscle, big)
                    rows.append(
                        {
                            "period": period,
                            "workout_id": wid,
                            "big_group": target_big,
                            "fine_muscle": target_muscle,
                            "set_factor": factor * 1.0,  # 主肌肉权重
                            "volume": vol * 1.0,
                        }
                    )

        # other_muscles 作为 secondary，权重从设置获取
        om_str = row.get("other_muscles", "") or ""
        if isinstance(om_str, str) and om_str.strip():
            for m in om_str.split(";"):
                m = m.strip()
                if m and m in MUSCLE_TO_GROUP:
                    big = MUSCLE_TO_GROUP[m]
                    rows.append(
                        {
                            "period": period,
                            "workout_id": wid,
                            "big_group": big,
                            "fine_muscle": m,
                            "set_factor": factor * secondary_factor,
                            "volume": vol * secondary_factor,
                        }
                    )
                    # 如果该肌肉的数据需要计入其他肌肉
                    if m in MUSCLE_INCLUDES:
                        for target_muscle in MUSCLE_INCLUDES[m]:
                            target_big = MUSCLE_TO_GROUP.get(target_muscle, big)
                            rows.append(
                                {
                                    "period": period,
                                    "workout_id": wid,
                                    "big_group": target_big,
                                    "fine_muscle": target_muscle,
                                    "set_factor": factor * secondary_factor,
                                    "volume": vol * secondary_factor,
                                }
                            )

    if not rows:
        return pd.DataFrame(columns=["period_start", "big_group", "fine_muscle", "value"])

    mdf = pd.DataFrame(rows)

    # 贴回 workout_duration_min，用于 Duration 计算
    wd = df.groupby("workout_id")["workout_duration_min"].first()
    mdf = mdf.merge(wd.rename("workout_duration_min"), on="workout_id", how="left")

    if metric == "Workouts":
        # 先按 workout_id 和 fine_muscle 去重
        unique_workouts = mdf[["period", "big_group", "workout_id", "fine_muscle"]].drop_duplicates()
        grouped = unique_workouts.groupby(["period", "big_group", "fine_muscle"])["workout_id"].nunique()
    elif metric == "Duration":
        muscle_count = mdf.groupby(["period", "workout_id"])["fine_muscle"].nunique()
        mdf = mdf.join(muscle_count.rename("muscle_count"), on=["period", "workout_id"])
        mdf["duration_hours_share"] = (
            mdf["workout_duration_min"] / mdf["muscle_count"] / 60.0
        )
        grouped = mdf.groupby(["period", "big_group", "fine_muscle"])["duration_hours_share"].sum()
    elif metric == "Volume":
        grouped = mdf.groupby(["period", "big_group", "fine_muscle"])["volume"].sum()
    else:  # Sets
        grouped = mdf.groupby(["period", "big_group", "fine_muscle"])["set_factor"].sum()

    res = grouped.reset_index().rename(columns={"period": "period_start"})
    if "value" not in res.columns:
        val_col = [c for c in res.columns if c not in
                   ["period_start", "big_group", "fine_muscle"]][0]
        res = res.rename(columns={val_col: "value"})
    return res


# -----------------------------------
# 聚合：Top Exercises
# -----------------------------------

def epley_1rm(weight, reps):
    return weight * (1 + reps / 30.0)


def build_exercise_stats(df: pd.DataFrame, view_mode: str) -> pd.DataFrame:
    """
    返回每个 period + exercise 的统计。
    """
    period_col = "week_period" if view_mode == "Week" else "month_period"

    df = df.copy()
    df["period_start"] = df[period_col]
    df["est_1rm"] = epley_1rm(df["weight"], df["reps"])

    grouped = df.groupby(["period_start", "exercise_title"])

    stats = grouped.agg(
        total_sets=("metric_set_factor", "sum"),
        total_reps=("reps", "sum"),
        heaviest_weight=("weight", "max"),
        best_set_volume=("metric_set_volume", "max"),
        session_volume=("metric_set_volume", "sum"),
        max_estimated_1rm=("est_1rm", "max"),
    ).reset_index()

    prim = (
        df.groupby(["period_start", "exercise_title"])["primary_group"]
        .agg(lambda x: x.value_counts().index[0] if x.dropna().size > 0 else np.nan)
        .reset_index()
    )

    stats = stats.merge(prim, on=["period_start", "exercise_title"], how="left")
    return stats


def get_top_exercise_for_muscle(ex_stats: pd.DataFrame, muscle: str, period_start):
    """当前周期里，对某个 muscle 用 heaviest_weight 选一个 top exercise。"""
    current = ex_stats[
        (ex_stats["period_start"] == period_start)
        & (ex_stats["primary_group"] == muscle)
    ]
    if current.empty:
        return None
    idx = current["heaviest_weight"].idxmax()
    return current.loc[idx]


# -----------------------------------
# UI：Workout Summary
# -----------------------------------

def render_workout_summary(period_summary: pd.DataFrame, view_mode: str, metric_label: str):
    # Initialize independent metric state for Workout Summary
    if "workout_summary_metric" not in st.session_state:
        st.session_state.workout_summary_metric = metric_label
    
    current_metric = st.session_state.workout_summary_metric
    
    # Style for right-aligned compact button group with minimal gap
    st.markdown("""
        <style>
        /* Compact buttons with minimal gap */
        .st-key-ws_metric_btn_workouts button,
        .st-key-ws_metric_btn_duration button,
        .st-key-ws_metric_btn_volume button,
        .st-key-ws_metric_btn_sets button {
            min-width: 70px !important;
            white-space: nowrap !important;
            padding: 0.3rem 0.5rem !important;
            font-size: 0.85rem !important;
        }
        /* Reduce gap between button columns for Workout Summary */
        div[data-testid="column"]:has(.st-key-ws_metric_btn_workouts),
        div[data-testid="column"]:has(.st-key-ws_metric_btn_duration),
        div[data-testid="column"]:has(.st-key-ws_metric_btn_volume),
        div[data-testid="column"]:has(.st-key-ws_metric_btn_sets) {
            flex: 0 0 auto !important;
            width: auto !important;
            min-width: auto !important;
            padding-left: 3px !important;
            padding-right: 3px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Title and buttons on same row, buttons right-aligned
    title_col, btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([6, 1, 1, 1, 1], gap="small")
    
    with title_col:
        st.subheader("Workout Summary")
    with btn_col1:
        if st.button("Workouts", key="ws_metric_btn_workouts", type="primary" if current_metric == "Workouts" else "secondary"):
            if current_metric != "Workouts":
                st.session_state.workout_summary_metric = "Workouts"
                st.rerun()
    with btn_col2:
        if st.button("Duration", key="ws_metric_btn_duration", type="primary" if current_metric == "Duration" else "secondary"):
            if current_metric != "Duration":
                st.session_state.workout_summary_metric = "Duration"
                st.rerun()
    with btn_col3:
        if st.button("Volume", key="ws_metric_btn_volume", type="primary" if current_metric == "Volume" else "secondary"):
            if current_metric != "Volume":
                st.session_state.workout_summary_metric = "Volume"
                st.rerun()
    with btn_col4:
        if st.button("Sets", key="ws_metric_btn_sets", type="primary" if current_metric == "Sets" else "secondary"):
            if current_metric != "Sets":
                st.session_state.workout_summary_metric = "Sets"
                st.rerun()
    
    # Use the independent metric for this section
    metric_label = st.session_state.workout_summary_metric

    if period_summary.empty:
        st.info("No period summary data.")
        return None
    
    periods = period_summary["period_start"].sort_values(ascending=False).tolist()
    
    # 覆盖primary按钮颜色为蓝色，并完全移除所有焦点边框和效果
    st.markdown("""
        <style>
        button[kind="primary"] {
            background-color: #1f77b4 !important;
        }
        button[kind="primary"]:hover {
            background-color: #1a6ba3 !important;
        }
        button[kind="primary"]:focus,
        button[kind="primary"]:active,
        button[kind="primary"]:focus-visible,
        button[kind="primary"]:after {
            box-shadow: none !important;
            border: none !important;
            outline: none !important;
            border-color: transparent !important;
            border-width: 0 !important;
        }
        button[kind="secondary"]:focus,
        button[kind="secondary"]:active,
        button[kind="secondary"]:focus-visible,
        button[kind="secondary"]:after {
            box-shadow: none !important;
            outline: none !important;
        }
        button:focus-visible {
            outline: none !important;
        }
        /* 完全禁用所有按钮的focus效果 */
        button * {
            outline: none !important;
        }
        /* 针对Streamlit的base-web按钮组件 */
        [data-baseweb="button"]:focus,
        [data-baseweb="button"]:active,
        [data-baseweb="button"]:focus-visible {
            box-shadow: none !important;
            border: none !important;
            outline: none !important;
        }
        [data-baseweb="button"] * {
            outline: none !important;
        }
        /* 强制移除所有button的focus状态边框和轮廓，但保留默认边框 */
        button:focus, button:active, button:focus-visible {
            outline: 0 !important;
            outline-offset: 0 !important;
            box-shadow: 0 0 0 0 transparent !important;
        }
        /* 移除Streamlit按钮容器的focus效果，但保留边框 */
        div[data-testid="stButton"] button:focus,
        div[data-testid="stButton"] button:active {
            outline: none !important;
            box-shadow: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
    metric_col_map = {
        "Workouts": "workouts",
        "Duration": "duration_hours",
        "Volume": "volume",
        "Sets": "sets",
    }
    metric_col = metric_col_map[metric_label]
    
    # 单位映射
    weight_unit_suffix = get_weight_unit_suffix()
    metric_units = {
        "Workouts": "Times",
        "Duration": "Hours",
        "Volume": weight_unit_suffix,
        "Sets": "Sets",
    }
    metric_unit = metric_units[metric_label]

    periods = period_summary["period_start"].sort_values(ascending=False).tolist()
    
    # 交互式图表：使用 Plotly 来实现真正的点击交互
    chart_df = period_summary.copy()
    if metric_col == "volume":
        chart_df["volume"] = convert_volume_for_display(chart_df["volume"])
    # 计算周期结束日期（根据view_mode）
    if view_mode == "Week":
        chart_df["period_end"] = chart_df["period_start"].apply(lambda d: d + pd.Timedelta(days=6))
    else:  # Month
        chart_df["period_end"] = chart_df["period_start"].apply(
            lambda d: (d.replace(day=28) + pd.Timedelta(days=4)).replace(day=1) - pd.Timedelta(days=1)
        )
    # 日期范围格式：显示开始-结束 (MM/DD - MM/DD)
    chart_df["period_str"] = chart_df.apply(
        lambda row: f"{row['period_start'].strftime('%m/%d')} - {row['period_end'].strftime('%m/%d')}",
        axis=1
    )
    # X轴标签格式：Week视图显示W{实际周数}<br>MM/DD，Month视图显示Jan'24格式
    if view_mode == "Week":
        chart_df["x_label"] = chart_df["period_start"].apply(
            lambda d: f"W{d.isocalendar()[1]}<br>{d.strftime('%m/%d')}"
        )
    else:  # Month
        chart_df["x_label"] = chart_df["period_start"].apply(
            lambda d: d.strftime("%b'%y")
        )
    
    # 使用 Plotly 创建可点击的柱状图
    fig = go.Figure()
    
    # 添加柱子，颜色根据是否被选中来设置
    colors = ["#1f77b4" if p == st.session_state.active_period else "#d3d3d3" 
              for p in chart_df["period_start"]]
    
    # 根据metric类型自定义hover显示格式（显示Period标签和日期范围）
    hovertemplate = "%{customdata}<extra></extra>"

    def build_hover(row):
        period_line = f"Period: {row['period_str']}"
        metric_value = row[metric_col]
        if metric_label == "Workouts":
            count = int(round(metric_value))
            plural = "s" if count != 1 else ""
            value_line = f"Workouts: {count:,} Time{plural}"
        elif metric_label == "Duration":
            hours = int(metric_value)
            mins = int(round((metric_value - hours) * 60))
            value_line = f"Duration: {hours} h {mins:02d} min"
        elif metric_label == "Volume":
            converted = convert_volume_for_display(metric_value)
            value_line = f"Volume: {format_compact_number(converted)} {weight_unit_suffix}"
        else:
            sets_val = format_compact_number(metric_value, decimals=1)
            value_line = f"Sets: {sets_val} Sets"
        return f"<span style='text-align:left'>{period_line}<br>{value_line}</span>"

    hover_values = [build_hover(row) for _, row in chart_df.iterrows()]
    
    fig.add_trace(go.Bar(
        x=chart_df["x_label"],
        y=chart_df[metric_col],
        marker=dict(color=colors),
        hovertemplate=hovertemplate,
        customdata=hover_values,
        name="",
    ))
    
    fig.update_layout(
        title="",
        xaxis_title="",
        yaxis_title=metric_unit,
        height=300,
        margin=dict(l=50, r=10, t=20, b=60),
        hovermode='closest',
        plot_bgcolor="white",
        showlegend=False,
        xaxis=dict(
            tickangle=0,
            type='category',
            side='bottom',
        ),
        yaxis=dict(
            showticklabels=True,
            showgrid=True,
            zeroline=True,
            fixedrange=False,
            side='left',
        ),
        hoverlabel=dict(
            align='left'
        ),
    )
    
    chart_key = "workout_chart"
    st.plotly_chart(
        fig,
        use_container_width=True,
        key=chart_key,
        on_select="rerun",
        selection_mode="points",
        config={"displayModeBar": False},
    )

    def _get_selection(state_key: str):
        chart_state = st.session_state.get(state_key)
        if not chart_state:
            return None
        if isinstance(chart_state, dict):
            for attr in ("selection", "last_selection", "selection_state"):
                payload = chart_state.get(attr)
                if payload:
                    return payload
        return chart_state

    selection_payload = _get_selection(chart_key)

    def _extract_point_index(selection) -> int | None:
        if not selection:
            return None

        def _try_list(value):
            if isinstance(value, list) and value:
                return value[0]
            return None

        points = None;
        if isinstance(selection, dict):
            points = selection.get("points") or selection.get("selected_points")
        else:
            points = getattr(selection, "points", None) or getattr(selection, "selected_points", None)

        if points:
            point_info = points[0]
            if isinstance(point_info, dict):
                for key in ("point_index", "pointIndex", "point_number", "pointNumber", "point"):
                    if key in point_info:
                        return point_info[key]
            else:
                for key in ("point_index", "pointIndex", "point_number", "pointNumber", "point"):
                    value = getattr(point_info, key, None)
                    if value is not None:
                        return value

        # fallback to aggregated arrays on the selection payload
        candidates = []
        if isinstance(selection, dict):
            candidates = [
                selection.get("point_indices"),
                selection.get("pointIndexes"),
                selection.get("pointNumbers"),
                selection.get("point_numbers"),
            ]
        else:
            candidates = [
                getattr(selection, "point_indices", None),
                getattr(selection, "pointIndexes", None),
                getattr(selection, "pointNumbers", None),
                getattr(selection, "point_numbers", None),
            ]
        for candidate in candidates:
            value = _try_list(candidate)
            if value is not None:
                return value
        return None

    point_index = _extract_point_index(selection_payload)
    if point_index is not None and 0 <= point_index < len(chart_df):
        clicked_period = chart_df.iloc[int(point_index)]["period_start"]
        if clicked_period != st.session_state.active_period:
            update_active_period(clicked_period)
            st.rerun()
    
    # 四个指标卡片（网格布局）
    # 检查active_period是否在当前period_summary中，如果不在则使用最新的period
    filtered = period_summary[period_summary["period_start"] == st.session_state.active_period]
    if filtered.empty:
        # active_period不在当前视图的period列表中，使用最新的period
        update_active_period(periods[0])
        filtered = period_summary[period_summary["period_start"] == st.session_state.active_period]
    
    current_row = filtered.iloc[0]
    idx = period_summary.index[period_summary["period_start"] == st.session_state.active_period][0]
    prev_row = period_summary.iloc[idx - 1] if idx > period_summary.index.min() else None
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    cards = [
        ("Workouts", "workouts", "Times"),
        ("Duration", "duration_hours", "Hours"),
        ("Volume", "volume", weight_unit_suffix),
        ("Sets", "sets", "Sets"),
    ]
    for (title, col, unit), container in zip(cards, [c1, c2, c3, c4]):
        with container:
            cur_val = current_row[col]
            if prev_row is None:
                delta_str = "No previous period"
                delta_color = "#8a8f9c"
                abs_delta_str = ""
            else:
                prev_val = prev_row[col]
                abs_delta_value = cur_val - prev_val
                abs_delta_str = format_metric_abs_change(col, abs_delta_value)
                if prev_val == 0:
                    delta_str = "New" if cur_val > 0 else "No change"
                    delta_color = "#26c281" if cur_val > 0 else "#8a8f9c"
                else:
                    diff_pct = (cur_val - prev_val) / prev_val * 100
                    delta_str = f"{diff_pct:+.1f}%"
                    if diff_pct > 0:
                        delta_color = "#26c281"
                    elif diff_pct < 0:
                        delta_color = "#e45947"
                    else:
                        delta_color = "#8a8f9c"
                if not abs_delta_str:
                    abs_delta_str = format_metric_abs_change(col, cur_val - prev_val)

            if col == "duration_hours":
                hours = int(cur_val)
                mins = int(round((cur_val - hours) * 60))
                cur_display = f"{hours}h {mins:02d}m"
            elif col == "volume":
                converted_val = convert_volume_for_display(cur_val)
                value_str = format_compact_number(converted_val)
                cur_display = f"{value_str} <span style='font-size: 0.7em;'>{unit}</span>"
            elif col == "sets":
                value_str = format_compact_number(cur_val, decimals=1)
                cur_display = f"{value_str} <span style='font-size: 0.7em;'>{unit}</span>"
            else:  # workouts
                value_str = f"{int(round(cur_val)):,}"
                cur_display = f"{value_str} <span style='font-size: 0.7em;'>{unit}</span>"

            # Build single HTML block so padding wraps all content (Streamlit creates separate containers per st.markdown)
            title_html = f"<div style='font-size: 0.95rem; font-weight: 600; margin-bottom: 5px;'>{title}</div>"
            value_html = f"<h3 style='margin-top: 0px; margin-bottom: 5px;'>{cur_display}</h3>"
            delta_html = ""
            if delta_str:
                if prev_row is None:
                    display_delta = delta_str
                else:
                    pct_part = delta_str if delta_str not in ("New", "No change") else ""
                    if pct_part:
                        display_delta = f"{abs_delta_str} ({pct_part})"
                    else:
                        display_delta = abs_delta_str or delta_str
                        if delta_str in ("New", "No change"):
                            display_delta = f"{abs_delta_str} {delta_str}".strip()
                delta_html = f"<span style='color: {delta_color}; font-size: 0.875rem;'>{display_delta}</span>"

            wrapped = f"<div style='padding-left: 50px;'>{title_html}{value_html}{delta_html}</div>"
            st.markdown(wrapped, unsafe_allow_html=True)


# -----------------------------------
# UI：Muscle Training Heatmap
# -----------------------------------

# -----------------------------------
# UI：Muscle Distribution（蛛网 + 细肌肉条形图）
# -----------------------------------

def render_muscle_distribution(df: pd.DataFrame,
                               muscle_df: pd.DataFrame,
                               detail_df: pd.DataFrame,
                               metric: str,
                               active_period,
                               raw_hevy_df: pd.DataFrame = None):
    """Render muscle distribution with radar chart and detailed breakdown."""
    if muscle_df.empty or active_period is None:
        st.info("No muscle distribution data.")
        return
    
    # Initialize session state for distribution metric
    if "distribution_metric" not in st.session_state:
        st.session_state.distribution_metric = "Sets"
    
    current_metric = st.session_state.distribution_metric
    
    # Style for right-aligned compact button group with minimal gap
    st.markdown("""
        <style>
        /* Compact buttons with minimal gap */
        .st-key-metric_btn_sets button,
        .st-key-metric_btn_volume button,
        .st-key-metric_btn_workouts button {
            min-width: 70px !important;
            white-space: nowrap !important;
            padding: 0.3rem 0.5rem !important;
            font-size: 0.85rem !important;
        }
        /* Reduce gap between button columns for Muscle Distribution */
        div[data-testid="column"]:has(.st-key-metric_btn_sets),
        div[data-testid="column"]:has(.st-key-metric_btn_volume),
        div[data-testid="column"]:has(.st-key-metric_btn_workouts) {
            flex: 0 0 auto !important;
            width: auto !important;
            min-width: auto !important;
            padding-left: 3px !important;
            padding-right: 3px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Title and buttons on same row, buttons right-aligned
    title_col, btn_col1, btn_col2, btn_col3 = st.columns([7, 1, 1, 1], gap="small")
    
    with title_col:
        st.markdown('<h3 id="muscle-distribution">Muscle Distribution</h3>', unsafe_allow_html=True)
    with btn_col1:
        if st.button("Sets", key="metric_btn_sets", type="primary" if current_metric == "Sets" else "secondary"):
            if current_metric != "Sets":
                st.session_state.distribution_metric = "Sets"
                st.rerun()
    with btn_col2:
        if st.button("Volume", key="metric_btn_volume", type="primary" if current_metric == "Volume" else "secondary"):
            if current_metric != "Volume":
                st.session_state.distribution_metric = "Volume"
                st.rerun()
    with btn_col3:
        if st.button("Workouts", key="metric_btn_workouts", type="primary" if current_metric == "Workouts" else "secondary"):
            if current_metric != "Workouts":
                st.session_state.distribution_metric = "Workouts"
                st.rerun()
    
    # Check for unconfigured custom exercises and show warning
    if raw_hevy_df is not None:
        unconfigured_exercises = get_unconfigured_custom_exercises(raw_hevy_df)
        if unconfigured_exercises:
            count = len(unconfigured_exercises)
            exercise_list = ", ".join(unconfigured_exercises[:3])
            if count > 3:
                exercise_list += f" ... (+{count - 3} more)"
            if st.button(
                f"⚠️ {count} custom exercise(s) not configured: {exercise_list}. Click to configure.",
                key="home_unconfigured_warning",
                type="tertiary",
            ):
                st.session_state["nav_page"] = "Settings"
                st.rerun()
    
    muscle_df = muscle_df.copy()
    detail_df = detail_df.copy()
    metric_label = metric
    if metric == "Volume":
        suffix = get_weight_unit_suffix()
        metric_label = f"{metric} ({suffix})"
        if "value" in muscle_df.columns:
            muscle_df["value"] = convert_volume_for_display(muscle_df["value"])
        if "value" in detail_df.columns:
            detail_df["value"] = convert_volume_for_display(detail_df["value"])
    
    # ---------- 大肌群雷达图 ----------
    periods = sorted(muscle_df["period_start"].unique(), reverse=True)
    
    # 如果active_period不在当前periods中，使用最新的period
    if active_period not in periods:
        active_period = periods[0] if periods else None
        if active_period is None:
            st.info("No muscle distribution data.")
            return
    
    current = muscle_df[muscle_df["period_start"] == active_period]
    idx = periods.index(active_period)
    prev_period = periods[idx + 1] if idx < len(periods) - 1 else None
    prev = (
        muscle_df[muscle_df["period_start"] == prev_period]
        if prev_period is not None
        else pd.DataFrame()
    )

    def ensure_muscle_rows(df, period):
        rows = []
        for m in RADAR_ORDER:
            sub = df[df["muscle_group"] == m]
            if sub.empty:
                rows.append({"period_start": period, "muscle_group": m, "value": 0.0})
            else:
                rows.append(sub.iloc[0].to_dict())
        return pd.DataFrame(rows)

    current_full = ensure_muscle_rows(current, active_period)
    prev_full = ensure_muscle_rows(prev, prev_period) if prev_period is not None else None

    categories = RADAR_ORDER + [RADAR_ORDER[0]]
    current_vals = (
        current_full.set_index("muscle_group").loc[RADAR_ORDER]["value"].tolist()
    )
    current_vals.append(current_vals[0])

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=current_vals,
            theta=categories,
            fill="toself",
            name=f"Current ({active_period})",
            fillcolor="rgba(79, 123, 255, 0.35)",
            line=dict(color="#4f7bff", width=2),
        )
    )

    if prev_full is not None:
        prev_vals = (
            prev_full.set_index("muscle_group").loc[RADAR_ORDER]["value"].tolist()
        )
        prev_vals.append(prev_vals[0])
        fig.add_trace(
            go.Scatterpolar(
                r=prev_vals,
                theta=categories,
                fill="toself",
                name=f"Previous ({prev_period})",
                fillcolor="rgba(154, 170, 206, 0.25)",
                line=dict(color="rgba(154, 170, 206, 0.65)", width=2, dash="dot"),
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                gridcolor="rgba(79, 123, 255, 0.12)",
                showline=False,
                linewidth=0.5,
            ),
            angularaxis=dict(
                direction="clockwise",
                rotation=90,
                gridcolor="rgba(79, 123, 255, 0.12)",
            ),
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        height=400,
        margin=dict(l=20, r=20, t=20, b=60),
    )
    
    # ---------- Muscle Training Heatmap ----------
    # 使用当前选择的 metric 渲染热力图
    
    # 准备热力图数据
    current_detail = detail_df[detail_df["period_start"] == active_period]
    prev_detail = detail_df[detail_df["period_start"] == prev_period] if prev_period else pd.DataFrame()
    
    # 构建细分肌肉数据字典（用于显示）
    muscle_values = {}
    previous_values = {}
    
    # 先添加细分肌肉
    if not current_detail.empty:
        for _, row in current_detail.iterrows():
            fine_muscle = row["fine_muscle"]
            value = float(row["value"])
            muscle_values[fine_muscle] = value
    
    # 添加上一周期的细分肌肉数据
    if not prev_detail.empty:
        for _, row in prev_detail.iterrows():
            fine_muscle = row["fine_muscle"]
            value = float(row["value"])
            previous_values[fine_muscle] = value
    
    # 如果没有细分数据，回退到大肌群
    if not muscle_values:
        current_data = muscle_df[muscle_df["period_start"] == active_period]
        prev_data = muscle_df[muscle_df["period_start"] == prev_period] if prev_period else pd.DataFrame()
        
        for muscle in MUSCLE_GROUPS:
            muscle_row = current_data[current_data["muscle_group"] == muscle]
            if not muscle_row.empty:
                muscle_values[muscle] = float(muscle_row["value"].iloc[0])
            else:
                muscle_values[muscle] = 0.0
        
        if not prev_data.empty:
            for muscle in MUSCLE_GROUPS:
                muscle_row = prev_data[prev_data["muscle_group"] == muscle]
                if not muscle_row.empty:
                    previous_values[muscle] = float(muscle_row["value"].iloc[0])
                else:
                    previous_values[muscle] = 0.0
    
    # 为tooltip准备所有metrics数据（Sets, Volume, Workouts）
    all_metrics_data = {}
    all_previous_data = {}  # 每个metric对应的上一期数据
    for metric_type in ["Sets", "Volume", "Workouts"]:
        # 构建该metric的detail_df
        temp_detail_df = build_detailed_muscle_distribution(df, st.session_state.view_mode, metric_type, st.session_state.week_start)
        
        # 获取该metric的periods并找到对应的active和prev period
        temp_periods = sorted(temp_detail_df["period_start"].unique(), reverse=True)
        
        # 找到与active_period匹配的period（考虑类型转换）
        temp_active_period = None
        temp_prev_period = None
        active_period_str = str(active_period)
        for i, p in enumerate(temp_periods):
            if str(p) == active_period_str:
                temp_active_period = p
                if i < len(temp_periods) - 1:
                    temp_prev_period = temp_periods[i + 1]
                break
        
        temp_current = temp_detail_df[temp_detail_df["period_start"] == temp_active_period] if temp_active_period is not None else pd.DataFrame()
        temp_prev = temp_detail_df[temp_detail_df["period_start"] == temp_prev_period] if temp_prev_period is not None else pd.DataFrame()
        
        # DEBUG: Print info for Workouts
        if metric_type == "Workouts":
            print(f"[DEBUG] Workouts - active_period: {active_period}, temp_active_period: {temp_active_period}, temp_prev_period: {temp_prev_period}")
            print(f"[DEBUG] Workouts - temp_periods: {temp_periods[:3] if len(temp_periods) > 3 else temp_periods}")
            print(f"[DEBUG] Workouts - temp_current muscles: {temp_current['fine_muscle'].unique().tolist() if not temp_current.empty else []}")
            print(f"[DEBUG] Workouts - temp_prev muscles: {temp_prev['fine_muscle'].unique().tolist() if not temp_prev.empty else []}")
        
        metric_values_temp = {}
        if not temp_current.empty:
            for _, row in temp_current.iterrows():
                fine_muscle = row["fine_muscle"]
                value = float(row["value"])
                # Volume需要转换单位
                if metric_type == "Volume":
                    value = convert_volume_for_display(value)
                metric_values_temp[fine_muscle] = value
        
        all_metrics_data[metric_type] = metric_values_temp
        
        # 计算该metric对应的上一期数据
        prev_values_temp = {}
        if not temp_prev.empty:
            for _, row in temp_prev.iterrows():
                fine_muscle = row["fine_muscle"]
                value = float(row["value"])
                # Volume需要转换单位
                if metric_type == "Volume":
                    value = convert_volume_for_display(value)
                prev_values_temp[fine_muscle] = value
        
        # DEBUG: Print prev data for Workouts
        if metric_type == "Workouts":
            print(f"[DEBUG] Workouts - prev_values_temp: {prev_values_temp}")
        
        all_previous_data[metric_type] = prev_values_temp
    
    # 热力图类型选择 - 使用 SVG overlay 方案
    heatmap_image_path = Path(__file__).parent / "muscle_anatomy.png"
    heatmap_svg_overlay_path = Path(__file__).parent / "muscle_heatmap_svg_overlay.html"
    heatmap_svg_path = Path(__file__).parent / "muscle_heatmap_svg.html"
    
    # 创建两列布局：雷达图 | 热力图
    radar_col, heatmap_col = st.columns([1, 2])
    
    # 在左列渲染雷达图
    with radar_col:
        st.plotly_chart(fig, use_container_width=True)
    
    # 在右列渲染热力图
    with heatmap_col:
        # 优先使用 SVG overlay 方案（图片 + SVG 路径叠加）
        if heatmap_image_path.exists() and heatmap_svg_overlay_path.exists():
            import base64
            with open(heatmap_image_path, "rb") as img_file:
                image_base64 = base64.b64encode(img_file.read()).decode("utf-8")
            
            with open(heatmap_svg_overlay_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # 将肌肉数据和图片注入到 HTML 中
            muscle_data_json = json.dumps(muscle_values)
            previous_data_json = json.dumps(previous_values) if previous_values else "null"
            all_metrics_json = json.dumps(all_metrics_data)
            all_previous_json = json.dumps(all_previous_data)
            
            html_with_data = html_content.replace(
                "BODY_IMAGE_PLACEHOLDER",
                image_base64
            ).replace(
                "MUSCLE_DATA_PLACEHOLDER",
                muscle_data_json
            ).replace(
                "PREVIOUS_DATA_PLACEHOLDER",
                previous_data_json
            ).replace(
                "METRICS_TYPE_PLACEHOLDER",
                json.dumps(metric)
            ).replace(
                "PERIOD_TYPE_PLACEHOLDER",
                json.dumps(st.session_state.view_mode)
            ).replace(
                "ALL_METRICS_PLACEHOLDER",
                all_metrics_json
            ).replace(
                "ALL_PREVIOUS_PLACEHOLDER",
                all_previous_json
            )
            
            # 使用 components.html 渲染
            components.html(html_with_data, height=450, scrolling=False)
        elif heatmap_svg_path.exists():
            # 使用纯 SVG 热力图（fallback）
            with open(heatmap_svg_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # 将肌肉数据注入到 HTML 中
            muscle_data_json = json.dumps(muscle_values)
            previous_data_json = json.dumps(previous_values) if previous_values else "null"
            all_metrics_json = json.dumps(all_metrics_data)
            all_previous_json = json.dumps(all_previous_data)
            
            html_with_data = html_content.replace(
                "MUSCLE_DATA_PLACEHOLDER",
                muscle_data_json
            ).replace(
                "PREVIOUS_DATA_PLACEHOLDER",
                previous_data_json
            ).replace(
                "METRICS_TYPE_PLACEHOLDER",
                json.dumps(metric)
            ).replace(
                "PERIOD_TYPE_PLACEHOLDER",
                json.dumps(st.session_state.view_mode)
            ).replace(
                "ALL_METRICS_PLACEHOLDER",
                all_metrics_json
            )
            
            # 使用 components.html 渲染
            components.html(html_with_data, height=450, scrolling=False)
        else:
            st.warning("Muscle heatmap visualization file not found.")


# -----------------------------------
# UI：Workout Log
# -----------------------------------

def render_workout_log(df: pd.DataFrame, view_mode: str, active_period):
    st.subheader("Workout Log")

    if df.empty:
        st.info("No data loaded.")
        return

    weight_unit_suffix = get_weight_unit_suffix()
    
    # Ensure date column is datetime
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    
    # Get workout dates
    workout_dates = set(df["date"].dt.date.unique())
    
    # Determine date range based on view mode
    if view_mode == "Week" and active_period:
        # For week view, show the specific week
        period_date = pd.to_datetime(active_period)
        start_date = period_date
        end_date = start_date + pd.Timedelta(days=6)
    elif view_mode == "Month" and active_period:
        # For month view, show the entire month
        period_date = pd.to_datetime(active_period)
        start_date = period_date.replace(day=1)
        # Get last day of month
        if period_date.month == 12:
            end_date = period_date.replace(day=31)
        else:
            end_date = (period_date.replace(month=period_date.month + 1, day=1) - pd.Timedelta(days=1))
    else:
        st.info("No active period selected.")
        return
    
    # Use independent selected date for each view mode
    selected_key = f"selected_workout_date_{view_mode.lower()}"
    if selected_key not in st.session_state or st.session_state[selected_key] is None:
        # Default to last workout date within the current display range if available.
        # If no workouts exist within the range, fall back to the displayed end_date.
        if not df.empty:
            # Find workouts inside the start/end range
            in_range = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]
            if not in_range.empty:
                last_date_in_range = in_range["date"].max().date()
                st.session_state[selected_key] = last_date_in_range
            else:
                st.session_state[selected_key] = pd.to_datetime(end_date).date()

    # Render calendar based on view mode (after selected_key is set so selected button shows)
    if view_mode == "Week":
        render_week_calendar(start_date, end_date, workout_dates)
    else:
        render_month_calendar(start_date, end_date, workout_dates)
    

    if st.session_state[selected_key]:
        selected_date = st.session_state[selected_key]
        # Format: Weekday, Month Day, Year, Start Time (am/pm)
        weekday = selected_date.strftime('%A')
        date_str = selected_date.strftime('%B %d, %Y')
        day_df = df[df["date"].dt.date == selected_date]
        if day_df.empty:
            st.write("No workouts logged for this day.")
        else:
            summary = (
                day_df.groupby(["workout_id", "title"]) 
                .agg(
                    date=("date", "first"),
                    duration_min=("workout_duration_min", "first"),
                    volume=("metric_set_volume", "sum"),
                    sets=("metric_set_factor", "sum"),
                )
                .reset_index()
            )

            for idx, (_, row) in enumerate(summary.iterrows()):
                # Add divider between multiple workouts on the same day
                if idx > 0:
                    st.divider()
                
                # Workout start time in am/pm
                workout_time = row["date"].strftime('%I:%M %p') if hasattr(row["date"], 'strftime') else ''
                st.markdown(f"""
### {weekday}, {date_str} · {workout_time}
""")

                volume_display = convert_volume_for_display(row["volume"])
                # Format duration as 1h 13min
                duration_min = row["duration_min"]
                hours = int(duration_min // 60)
                minutes = int(duration_min % 60)
                duration_str = f"{hours}h {minutes}min" if hours > 0 else f"{minutes}min"

                # Format volume with thousands separator
                volume_str = f"{int(volume_display):,} {weight_unit_suffix}"

                # Sets with 1 decimal
                sets_str = f"{row['sets']:.1f}"

                st.markdown(f"""
<div style='margin-bottom: 1.8em;'>
    <div style='font-size:1.15em; font-weight:600; margin-bottom:0.3em;'>{row['title']}</div>
    <div style='display:flex; gap:2.5em; justify-content:left;'>
        <div style='text-align:left;'>
            <div style='font-size:0.95em; color:#888; font-weight:500;'>Duration</div>
            <div style='font-size:1.7em; font-weight:700; margin-top:0.1em;'>{duration_str}</div>
        </div>
        <div style='text-align:left;'>
            <div style='font-size:0.95em; color:#888; font-weight:500;'>Volume</div>
            <div style='font-size:1.7em; font-weight:700; margin-top:0.1em;'>{volume_str}</div>
        </div>
        <div style='text-align:left;'>
            <div style='font-size:0.95em; color:#888; font-weight:500;'>Sets</div>
            <div style='font-size:1.7em; font-weight:700; margin-top:0.1em;'>{sets_str}</div>
        </div>
    </div>
    <div style='margin-top:1em;'>
        <div style='margin-top:0.3em;'>
""", unsafe_allow_html=True)
                # Show exercise breakdown: sets x exercise
                workout_exs = day_df[day_df["workout_id"] == row["workout_id"]]
                # Preserve exercise appearance order from the source (API/raw data)
                exercise_order = list(workout_exs["exercise_title"].drop_duplicates())
                # Build a small mapping of exercise -> sets so we can render in appearance order
                # Use metric-aware set factor so warmups can be included/excluded globally
                ex_agg = (
                    workout_exs.groupby("exercise_title").agg(sets=("metric_set_factor", "sum"))
                )
                ex_map = ex_agg["sets"].to_dict() if not ex_agg.empty else {}

                for ex_title in exercise_order:
                    sets_val = ex_map.get(ex_title, 0)
                    st.markdown(f"<div style='font-size:1.08em; margin-bottom:0.1em;'>{sets_val:.1f} x {ex_title}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)


def render_week_calendar(start_date, end_date, workout_dates):
    """Render a horizontal week calendar with workout days highlighted."""
    dates = pd.date_range(start_date, end_date, freq='D')
    
    # Initialize selected date if not exists
    key = "selected_workout_date_week"
    if key not in st.session_state:
        st.session_state[key] = None
    
    # Create columns for each day
    cols = st.columns(7)
    
    for idx, date in enumerate(dates):
        with cols[idx]:
            day_name = date.strftime('%a')[0]  # First letter of day name
            day_num = date.day
            has_workout = date.date() in workout_dates
            is_selected = st.session_state[key] == date.date()
            
            # Create button label
            label = f"{day_name}\n\n{day_num}"

            # Determine button type and disabled state
            # Selected: primary (blue), Has workout: secondary (gray), No workout: tertiary (white)
            if is_selected:
                button_type = "primary"
                disabled = False
            elif has_workout:
                button_type = "secondary"
                disabled = False
            else:
                button_type = "tertiary"
                disabled = True
            
            if st.button(label, key=f"day_{date.date()}", type=button_type, use_container_width=True, disabled=disabled):
                st.session_state[key] = date.date()
                st.rerun()


def render_month_calendar(start_date, end_date, workout_dates):
    """Render a month calendar grid with workout days highlighted."""
    # Get all dates in the month
    dates = pd.date_range(start_date, end_date, freq='D')
    
    # Find the first day of the month and pad to start on the correct weekday
    first_weekday = start_date.weekday()  # Monday = 0
    
    # Initialize selected date if not exists
    key = "selected_workout_date_month"
    if key not in st.session_state:
        st.session_state[key] = None
    
    # Display month header
    month_name = start_date.strftime('%B %Y')
    st.markdown(f"<h3 style='text-align: center; margin: 20px 0;'>{month_name}</h3>", unsafe_allow_html=True)
    
    # CSS for month calendar - make buttons circular and center them
    st.markdown("""
    <style>
    .month-calendar-container {
        max-width: 600px;
        margin: 0 auto;
    }
    div[data-testid="column"] .stVerticalBlock {
        align-items: center !important;
    }
    div[data-testid="column"] .stVerticalBlock .stButton {
        margin: 0 auto !important;
        display: block !important;
    }
    div[data-testid="column"] > div > div > button {
        width: 50px !important;
        height: 50px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        font-size: 14px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display weekday headers as disabled buttons
    header_cols = st.columns(7)
    weekdays = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
    for idx, day in enumerate(weekdays):
        with header_cols[idx]:
            st.button(day, key=f"weekday_{idx}", disabled=True, type="tertiary")
    
    # Create calendar grid
    all_cells = []
    
    # Add empty cells for days before the first of the month
    for _ in range(first_weekday):
        all_cells.append(None)
    
    # Add all days in the month
    for date in dates:
        all_cells.append(date)
    
    # Render calendar in rows of 7
    for week_start in range(0, len(all_cells), 7):
        week_cells = all_cells[week_start:week_start + 7]
        cols = st.columns(7)
        
        for idx, date in enumerate(week_cells):
            with cols[idx]:
                if date is None:
                    # Empty cell
                    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
                else:
                    day_num = date.day
                    has_workout = date.date() in workout_dates
                    is_selected = st.session_state[key] == date.date()
                    
                    # Determine button type and disabled state
                    # Selected: primary (blue), Has workout: secondary (gray), No workout: tertiary (white)
                    if is_selected:
                        button_type = "primary"
                        disabled = False
                    elif has_workout:
                        button_type = "secondary"
                        disabled = False
                    else:
                        button_type = "tertiary"
                        disabled = True
                    
                    if st.button(str(day_num), key=f"month_day_{date.date()}", type=button_type, disabled=disabled):
                        st.session_state[key] = date.date()
                        st.rerun()


# Top Exercises section removed per user request.


# -----------------------------------
# 主入口
# -----------------------------------

def fetch_hevy_workouts(api_key: str, progress_hook=None):
    """从Hevy API获取训练数据"""
    try:
        import requests
    except ImportError:
        return None, "请先安装 requests 库: pip install requests"
    
    url = "https://api.hevyapp.com/v1/workouts"
    headers = {
        "api-key": api_key,
        "accept": "application/json"
    }
    
    all_workouts = []
    page = 0
    page_size = 10  # Hevy API限制最大为10
    
    try:
        while True:
            params = {
                "page": page,
                "pageSize": page_size
            }

            response = requests.get(url, headers=headers, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()

            workouts_batch = data.get("workouts", []) if isinstance(data, dict) else []

            if progress_hook is not None:
                try:
                    progress_hook(page + 1, len(workouts_batch), len(all_workouts) + len(workouts_batch))
                except Exception:
                    pass

            if not workouts_batch:
                break

            all_workouts.extend(workouts_batch)

            if len(workouts_batch) < page_size:
                break

            page += 1

        return {"workouts": all_workouts}, None
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP错误: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return None, f"获取Hevy数据失败: {str(e)}"


def convert_hevy_api_to_csv_format(workouts_data):
    """将Hevy API格式转换为CSV格式"""
    rows = []
    metadata = {
        "skipped_duplicate_sets": 0,
        "duplicate_workouts": [],
        "total_sets": 0,
        "workouts_count": 0,
    }

    if not workouts_data or "workouts" not in workouts_data:
        return pd.DataFrame(), metadata

    workout_ids = set()
    duplicate_workouts = set()
    seen_set_keys = set()
    skipped_duplicate_sets = 0

    for workout in workouts_data["workouts"]:
        workout_id = workout.get("id", "unknown")

        if workout_id in workout_ids:
            duplicate_workouts.add(workout_id)
            continue
        workout_ids.add(workout_id)

        title = workout.get("title", "Untitled")
        start_time = workout.get("start_time")
        end_time = workout.get("end_time")

        body_weight = workout.get("body_weight") or workout.get("bodyweight") or workout.get("user_body_weight")

        for exercise in workout.get("exercises", []):
            exercise_title = exercise.get("title", "Unknown")
            sets_list = exercise.get("sets", [])

            exercise_body_weight = exercise.get("body_weight") or exercise.get("bodyweight")

            for set_data in sets_list:
                weight = set_data.get("weight_kg")
                if weight is None:
                    weight = set_data.get("weight", 0)

                try:
                    weight = float(weight) if weight else 0
                except (ValueError, TypeError):
                    weight = 0

                reps = set_data.get("reps", 0)
                try:
                    reps = int(reps) if reps else 0
                except (ValueError, TypeError):
                    reps = 0

                set_index = set_data.get("index")
                set_uuid = set_data.get("id") or set_data.get("set_id") or set_data.get("uuid")
                raw_set_type = set_data.get("set_type") or set_data.get("type") or set_data.get("setType")

                set_type = raw_set_type
                if set_type is None:
                    if set_data.get("warmup") or set_data.get("is_warmup"):
                        set_type = "warmup"
                    else:
                        set_type = "normal"

                final_body_weight = exercise_body_weight if exercise_body_weight is not None else body_weight
                if final_body_weight is not None:
                    try:
                        final_body_weight = float(final_body_weight)
                    except (ValueError, TypeError):
                        final_body_weight = None

                if set_uuid:
                    unique_key = ("id", workout_id, set_uuid)
                elif set_index is not None:
                    unique_key = ("index", workout_id, exercise_title, set_index)
                else:
                    unique_key = None

                if unique_key is not None and unique_key in seen_set_keys:
                    skipped_duplicate_sets += 1
                    continue

                if unique_key is not None:
                    seen_set_keys.add(unique_key)

                # Extract duration and distance if present in API payload
                duration_val = set_data.get("duration_seconds")
                if duration_val is None:
                    # common alternatives
                    duration_val = set_data.get("duration_ms") or set_data.get("duration")
                # normalize duration: handle hh:mm:ss strings and ms values
                dur_seconds = None
                if duration_val is not None and duration_val != "":
                    try:
                        if isinstance(duration_val, str) and ":" in duration_val:
                            parts = [int(p) for p in duration_val.split(":")]
                            # support H:M:S or M:S
                            if len(parts) == 3:
                                dur_seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
                            elif len(parts) == 2:
                                dur_seconds = parts[0] * 60 + parts[1]
                            else:
                                dur_seconds = int(parts[0])
                        else:
                            # numeric-ish: if very large, treat as ms
                            dv = float(duration_val)
                            if dv > 100000:  # >100k -> assume ms
                                dur_seconds = int(dv / 1000)
                            else:
                                dur_seconds = int(dv)
                    except Exception:
                        dur_seconds = None

                # Distance fields
                distance_km = None
                if "distance_km" in set_data:
                    try:
                        distance_km = float(set_data.get("distance_km"))
                    except Exception:
                        distance_km = None
                else:
                    # common alternatives
                    dist = set_data.get("distance") or set_data.get("distance_miles") or set_data.get("distance_m")
                    if dist is not None and dist != "":
                        try:
                            dv = float(dist)
                            # if key suggests miles, convert
                            if set_data.get("distance_miles") is not None or (isinstance(dist, str) and "mi" in str(dist).lower()):
                                distance_km = dv * MI_TO_KM
                            else:
                                # assume kilometers if value reasonable (<1000)
                                if dv > 1000:
                                    # maybe meters -> convert to km
                                    distance_km = dv / 1000.0
                                else:
                                    distance_km = dv
                        except Exception:
                            distance_km = None

                row = {
                    "title": title,
                    "start_time": start_time,
                    "end_time": end_time,
                    "exercise_title": exercise_title,
                    "set_type": set_type,
                    "weight_kg": weight,
                    "reps": reps,
                    "set_index": set_index,
                    "set_uuid": set_uuid,
                    "body_weight": final_body_weight,
                    "duration_seconds": dur_seconds,
                    "distance_km": distance_km,
                }
                rows.append(row)

    df = pd.DataFrame(rows)

    metadata["skipped_duplicate_sets"] = skipped_duplicate_sets
    metadata["duplicate_workouts"] = sorted(duplicate_workouts)
    metadata["total_sets"] = len(df)
    metadata["workouts_count"] = len(workout_ids)

    return df, metadata


def summarize_raw_sets(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {"total_sets": 0, "workouts_count": 0}

    summary = {"total_sets": int(len(df)), "workouts_count": 0}
    if {"title", "start_time"}.issubset(df.columns):
        summary["workouts_count"] = (
            df[["title", "start_time"]].drop_duplicates().shape[0]
        )
    else:
        summary["workouts_count"] = df["title"].nunique()
    return summary


def store_dataset(source: str, df: pd.DataFrame, meta: dict, success_message: str, warnings=None, switch_to_source: bool = True):
    st.session_state["data_cache"][source] = df
    meta = dict(meta) if meta is not None else {}
    meta["success_message"] = success_message
    meta["status_messages"] = [warn for warn in (warnings or []) if warn]
    st.session_state["data_source_meta"][source] = meta
    if switch_to_source:
        st.session_state["data_source_choice"] = source
        st.session_state["pending_source_choice"] = source
    st.session_state["header_messages"] = []


def process_csv_upload(uploaded_file, key_prefix: str = "", switch_to_source: bool = False):
    if uploaded_file is None:
        return

    df = load_hevy_workouts(uploaded_file)
    df, measurement_info = normalize_measurement_units(df)
    summary = summarize_raw_sets(df)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    meta = {
        **summary,
        "updated_at": timestamp,
        "skipped_duplicate_sets": 0,
        "duplicate_workouts": [],
        "measurement_info": measurement_info,
    }
    file_name = getattr(uploaded_file, "name", None)
    if file_name:
        meta["file_name"] = file_name
    store_dataset(
        "Upload CSV File",
        df,
        meta,
        f"Loaded {summary['total_sets']} sets from CSV",
        switch_to_source=switch_to_source,
    )
    if switch_to_source:
        trigger_rerun()


def process_api_fetch(api_key: str, progress_hook=None) -> bool:
    api_key = (api_key or "").strip()
    if not api_key:
        st.session_state["header_messages"] = [("error", "Hevy API key is required to fetch data.")]
        return False

    data, error = fetch_hevy_workouts(api_key, progress_hook=progress_hook)
    if error:
        st.session_state["header_messages"] = [("error", error)]
        return False

    if not data:
        st.session_state["header_messages"] = [("warning", "No workout data returned from Hevy.")]
        return False

    df, meta = convert_hevy_api_to_csv_format(data)
    df, measurement_info = normalize_measurement_units(df)
    meta["measurement_info"] = measurement_info
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    meta["updated_at"] = timestamp

    success_message = f"Fetched {meta['total_sets']} sets from Hevy API"

    store_dataset(
        "Connect to Hevy API",
        df,
        meta,
        success_message,
        None,
    )
    return True


def schedule_api_fetch(api_key: str):
    """Queue a Hevy API fetch to run on the next app cycle."""
    api_key = (api_key or "").strip()
    if not api_key:
        st.session_state.setdefault("header_messages", [])
        st.session_state["header_messages"].append(
            ("error", "Hevy API key is required to fetch data."),
        )
        return

    remember_choice = st.session_state.get("remember_api_key")
    if remember_choice:
        st.session_state["api_key_value"] = api_key
    else:
        st.session_state["api_key_value"] = ""
    sync_persisted_api_key(api_key, bool(remember_choice))
    st.session_state["pending_api_key"] = api_key
    st.session_state["pending_fetch"] = api_key
    st.session_state["fetch_progress"] = ["Connecting to Hevy API"]
    trigger_rerun()


def render_remember_api_option(widget_key: str) -> bool:
    """Render the remember-API checkbox and sync it across UI contexts."""
    remember_current = st.session_state.get("remember_api_key", False)
    new_choice = st.checkbox(
        "Remember this API key",
        value=remember_current,
        key=widget_key,
        help="Stores the key in this browser session so you don't need to re-enter it next time. Disable on shared devices.",
    )
    if new_choice != remember_current:
        if new_choice:
            st.session_state["remember_api_key"] = True
            candidate_key = st.session_state.get("pending_api_key") or st.session_state.get("api_key_value", "")
            if candidate_key:
                st.session_state["api_key_value"] = candidate_key
            sync_persisted_api_key(candidate_key, True)
        else:
            clear_saved_api_key_state(clear_pending=True)
    elif new_choice:
        st.session_state["remember_api_key"] = True
    return new_choice


def render_empty_state():
    """Render the welcome screen when no data is loaded - styled consistently with Settings page."""
    
    # CSS for consistent card styling
    st.markdown("""
    <style>
    /* Welcome page upload button styling */
    .st-key-welcome_csv_upload [data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }
    .st-key-welcome_csv_upload [data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
        padding: 0 !important;
        height: auto !important;
        min-height: auto !important;
        border: none !important;
        gap: 0 !important;
    }
    .st-key-welcome_csv_upload .e16n7gab6 {
        width: 100% !important;
    }
    .st-key-welcome_csv_upload [data-testid="stBaseButton-secondary"] {
        width: 100% !important;
        border: 1px solid rgba(49, 51, 63, 0.2) !important;
        background-color: white !important;
        font-size: 0 !important;
        line-height: 1.6 !important;
        padding: 0.5rem 0.75rem !important;
    }
    .st-key-welcome_csv_upload [data-testid="stBaseButton-secondary"]::before {
        content: "📁 Choose File" !important;
        font-size: 14px !important;
        font-family: "Source Sans Pro", sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🚀 Get Started")
    st.caption("Choose one of the methods below to load your workout data and start exploring.")
    
    st.markdown("")
    
    col1, col2 = st.columns(2)
    
    # ===== Card 1: Upload CSV =====
    with col1:
        with st.container(border=True):
            st.markdown("**📁 Upload CSV File**")
            st.caption("Export from Hevy app and upload here")
            
            st.markdown("")
            
            uploaded_file = st.file_uploader(
                "Upload CSV",
                type=["csv"],
                key="welcome_csv_upload",
                label_visibility="collapsed",
            )
            if uploaded_file is not None:
                process_csv_upload(uploaded_file, switch_to_source=True)
    
    # ===== Card 2: Connect API =====
    with col2:
        with st.container(border=True):
            col_label, col_input = st.columns([1, 1.5])
            with col_label:
                st.markdown("**🔗 Connect Hevy API**")
                st.caption("Fetch directly from Hevy (Pro)")
            with col_input:
                api_key = st.text_input(
                    "API Key",
                    type="password",
                    value=st.session_state.get("pending_api_key", ""),
                    key="welcome_api_key",
                    placeholder="Enter API key",
                    label_visibility="collapsed",
                )
                if api_key != st.session_state.get("pending_api_key", ""):
                    st.session_state["pending_api_key"] = api_key
                render_remember_api_option("welcome_remember_api_checkbox")
            
            if st.button("🔗 Fetch", key="welcome_fetch_button", use_container_width=True):
                schedule_api_fetch(st.session_state.get("pending_api_key", ""))


def render_home_floating_controls(periods):
    """Render a compact floating toolbar with minimal labeling."""
    if st.session_state.get("nav_page") != "Home":
        return

    view_options = ["Week", "Month"]
    metric_options = ["Workouts", "Duration", "Volume", "Sets"]
    current_view = st.session_state.get("view_mode", "Week")
    current_metric = st.session_state.get("summary_metric", "Workouts")
    active_period = st.session_state.get("active_period")

    toolbar_shell = st.container()
    with toolbar_shell:
        st.markdown("<div class='floating-toolbar-anchor'></div>", unsafe_allow_html=True)
        # toolbar debug message removed

        col_view, col_period = st.columns([1, 2.5])

        with col_view:
            st.markdown("<div class='toolbar-chip' data-chip='vm'>View Mode</div>", unsafe_allow_html=True)
            view_shell = st.container()
            with view_shell:
                st.markdown("<div class='toolbar-control-shell'>", unsafe_allow_html=True)
                view_choice = st.selectbox(
                    "View Mode",
                    view_options,
                    index=view_options.index(current_view) if current_view in view_options else 0,
                    key="floating_view_selector",
                    label_visibility="collapsed",
                )
                if view_choice != current_view:
                    # persist current active_period for the current view
                    try:
                        st.session_state[f"active_period_{current_view.lower()}"] = st.session_state.get("active_period")
                    except Exception:
                        pass
                    # restore active_period for the newly selected view if available
                    saved = st.session_state.get(f"active_period_{view_choice.lower()}")
                    if saved is not None:
                        st.session_state["active_period"] = saved
                    # update view and rerun
                    st.session_state.view_mode = view_choice
                    trigger_rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        with col_period:
            st.markdown("<div class='toolbar-chip' data-chip='pr'>Selected Period</div>", unsafe_allow_html=True)
            period_shell = st.container()
            with period_shell:
                st.markdown("<div class='toolbar-period-shell'>", unsafe_allow_html=True)
                if not periods or active_period not in periods:
                    st.markdown("<div class='toolbar-period-display'>—</div>", unsafe_allow_html=True)
                else:
                    # Wrap period navigation in try/except so toolbar doesn't crash
                    try:
                        period_labels = {
                            p: describe_period_range(p, st.session_state.get("view_mode", "Week"))
                            for p in periods
                        }
                        active_idx = periods.index(active_period)
                        period_select_key = "floating_period_select"
                        nav_cols = st.columns([0.25, 1.5, 0.25])

                        with nav_cols[0]:
                            # Left arrow: go to older period (higher index in descending list)
                            disable_prev = active_idx >= len(periods) - 1
                            if st.button(
                                "←",
                                key="floating_period_prev",
                                disabled=disable_prev,
                                use_container_width=True,
                            ):
                                if active_idx < len(periods) - 1:
                                    new_period = periods[active_idx + 1]
                                    # log debug info
                                    st.session_state["toolbar_last_action"] = ("left", str(new_period))
                                    # Set a temporary target so on next render we
                                    # initialize the selectbox with the new value,
                                    # and update active_period immediately so the
                                    # selectbox won't revert the change on render.
                                    st.session_state["floating_period_target"] = new_period
                                    try:
                                        update_active_period(new_period)
                                    except Exception:
                                        # update_active_period is defensive, ignore errors
                                        pass
                                    trigger_rerun()

                        with nav_cols[1]:
                            # Make sure the floating selectbox reflects the current
                            # active_period on render to avoid stale widget values
                            # reverting arrow navigation.
                            # If an arrow set a temporary target, apply it now so
                            # the selectbox is created with the desired value.
                            if "floating_period_target" in st.session_state:
                                st.session_state[period_select_key] = st.session_state.pop("floating_period_target")
                            elif period_select_key not in st.session_state:
                                # Initialize only if missing
                                st.session_state[period_select_key] = st.session_state.get("active_period")

                            selected_period = st.selectbox(
                                "Period",
                                periods,
                                index=active_idx,
                                format_func=lambda p: period_labels[p],
                                key=period_select_key,
                                label_visibility="collapsed",
                            )
                            # If the selectbox changed, update via helper and rerun once
                            if selected_period != st.session_state.get("active_period"):
                                st.session_state["toolbar_last_action"] = ("select", str(selected_period))
                                update_active_period(selected_period)
                                trigger_rerun()

                        with nav_cols[2]:
                            # Right arrow: go to newer period (lower index in descending list)
                            disable_next = active_idx <= 0
                            if st.button(
                                "→",
                                key="floating_period_next",
                                disabled=disable_next,
                                use_container_width=True,
                            ):
                                if active_idx > 0:
                                    new_period = periods[active_idx - 1]
                                    # log debug info for right arrow
                                    st.session_state["toolbar_last_action"] = ("right", str(new_period))
                                    st.session_state["floating_period_target"] = new_period
                                    try:
                                        update_active_period(new_period)
                                    except Exception:
                                        pass
                                    trigger_rerun()
                    except Exception as e:
                        # Show a non-fatal error inside the toolbar so the rest of the page can render
                        st.markdown(
                            f"<div style='color: red; font-weight:600;'>Toolbar error: {str(e)}</div>",
                            unsafe_allow_html=True,
                        )
                        # also write the traceback to session for later inspection
                        import traceback

                        tb = traceback.format_exc()
                        st.text("Debug Trace:")
                        st.text(tb)
                st.markdown("</div>", unsafe_allow_html=True)

    if STREAMLIT_FLOAT_READY:
        toolbar_shell.float(
            "bottom: 14px; "
            "right: 24px; "
            "left: auto; "
            "width: 420px; "
            "padding-left: 0.75rem; "
            "padding-right: 0.75rem; "
            "box-sizing: border-box; "
            "transform: none; "
            "z-index: 1600;"
        )


def main():
    page_titles = {
        "Workouts Review": "Workouts Review",
        "Exercise Review": "Hevy Data Analyzer – Exercise Review",
        "Settings": "Hevy Data Analyzer – Settings",
    }

    nav_items = [
        ("Home", "🏠", "Home"),
        ("Workouts Review", "📈", "Workouts Review"),
        ("Exercise Review", "💪", "Exercise Review"),
        ("Settings", "⚙️", "Settings"),
    ]

    if "nav_page" not in st.session_state:
        st.session_state["nav_page"] = "Home"
    if "prev_nav_page" not in st.session_state:
        st.session_state["prev_nav_page"] = "Home"
    if "data_source_choice" not in st.session_state:
        st.session_state["data_source_choice"] = "Connect to Hevy API"
    if "data_cache" not in st.session_state:
        st.session_state["data_cache"] = {}
    if "data_source_meta" not in st.session_state:
        st.session_state["data_source_meta"] = {}
    if "header_messages" not in st.session_state:
        st.session_state["header_messages"] = []

    persisted_key = None
    if "remember_api_key" not in st.session_state or "api_key_value" not in st.session_state:
        persisted_key = load_persisted_api_key()
    if "remember_api_key" not in st.session_state:
        st.session_state["remember_api_key"] = bool(persisted_key)
    if "api_key_value" not in st.session_state:
        st.session_state["api_key_value"] = (
            persisted_key if st.session_state.get("remember_api_key") else ""
        )

    user_prefs = load_user_preferences()
    if "pending_api_key" not in st.session_state:
        st.session_state["pending_api_key"] = (
            st.session_state.get("api_key_value", "")
            if st.session_state.get("remember_api_key")
            else ""
        )
    if "pending_source_choice" not in st.session_state:
        st.session_state["pending_source_choice"] = st.session_state["data_source_choice"]
    if "body_weight_setting" not in st.session_state:
        st.session_state.body_weight_setting = float(user_prefs.get("body_weight", 85.0))
    if "week_start" not in st.session_state:
        st.session_state.week_start = user_prefs.get("week_start", "Monday")
    if "weight_unit_preference" not in st.session_state:
        st.session_state["weight_unit_preference"] = user_prefs.get("weight_unit", "kg")
    if "distance_unit_preference" not in st.session_state:
        st.session_state["distance_unit_preference"] = user_prefs.get("distance_unit", "kilometers")
    # Calculation settings
    if "include_warmup_sets" not in st.session_state:
        st.session_state["include_warmup_sets"] = user_prefs.get("include_warmup_sets", False)
    if "secondary_muscle_factor" not in st.session_state:
        st.session_state["secondary_muscle_factor"] = user_prefs.get("secondary_muscle_factor", 0.5)
    if "drop_set_factor" not in st.session_state:
        st.session_state["drop_set_factor"] = user_prefs.get("drop_set_factor", 0.5)
    if "include_bodyweight" not in st.session_state:
        st.session_state["include_bodyweight"] = user_prefs.get("include_bodyweight", True)
    if "pending_fetch" not in st.session_state:
        st.session_state["pending_fetch"] = None
    if "fetch_progress" not in st.session_state:
        st.session_state["fetch_progress"] = []
    if "csv_upload_pending" not in st.session_state:
        st.session_state["csv_upload_pending"] = False
    if "source_panel_open" not in st.session_state:
        st.session_state["source_panel_open"] = False

    pending_key = st.session_state.get("pending_fetch")
    if pending_key:
        overlay_placeholder = st.empty()
        progress_lines = st.session_state.get("fetch_progress") or ["Connecting to Hevy API"]
        overlay_placeholder.markdown(
            build_fetch_overlay(progress_lines),
            unsafe_allow_html=True,
        )

        def progress_hook(page_number: int, workouts_count: int, total_count: int):
            if workouts_count == 0:
                message = f"Page {page_number}: no workouts returned"
            else:
                message = f"Page {page_number}: {workouts_count} workouts fetched (total {total_count})"
            progress_list = st.session_state.get("fetch_progress", [])
            progress_list.append(message)
            st.session_state["fetch_progress"] = progress_list
            overlay_placeholder.markdown(
                build_fetch_overlay(progress_list),
                unsafe_allow_html=True,
            )

        success = process_api_fetch(pending_key, progress_hook=progress_hook)
        st.session_state["pending_fetch"] = None
        st.session_state["fetch_progress"] = []
        overlay_placeholder.empty()

        if not success:
            trigger_rerun()
            st.stop()

        trigger_rerun()
        st.stop()

    with st.sidebar:
        st.markdown("<div class='sidebar-brand'>HEVY ANALYZER</div>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-note'>Visualize and audit your training data.</div>", unsafe_allow_html=True)
        sidebar_data_cache = st.session_state["data_cache"]
        sidebar_current_source = st.session_state["data_source_choice"]
        sidebar_raw_df = sidebar_data_cache.get(sidebar_current_source)
        sidebar_has_data = sidebar_raw_df is not None and not sidebar_raw_df.empty

        # Navigation items with collapsible Home submenu
        for key, icon, label in nav_items:
            active = st.session_state["nav_page"] == key
            
            # Main menu item
            if active:
                st.markdown(
                    f"<div class='sidebar-nav-active'><span class='icon'>{icon}</span>{label}</div>",
                    unsafe_allow_html=True,
                )
            else:
                if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
                    st.session_state["nav_page"] = key
                    trigger_rerun()

    # If a workout was linked via query params, ensure we open the Workouts Review page
    params = st.query_params
    if params.get("selected_workout_id"):
        st.session_state["nav_page"] = "Workouts Review"

    page = st.session_state["nav_page"]
    
    # Scroll to top when page changes
    if page != st.session_state.get("prev_nav_page"):
        st.session_state["prev_nav_page"] = page
        # Use components.html with delayed scroll for reliability
        components.html(
            """
            <script>
                (function scrollToTop() {
                    // Immediate scroll attempt
                    function doScroll() {
                        const mainEl = window.parent.document.querySelector('section.main');
                        if (mainEl) {
                            mainEl.scrollTop = 0;
                        }
                        const stMain = window.parent.document.querySelector('[data-testid="stMain"]');
                        if (stMain) {
                            stMain.scrollTop = 0;
                        }
                        window.parent.scrollTo(0, 0);
                    }
                    
                    // Execute immediately
                    doScroll();
                    
                    // Also execute after delays to catch late renders
                    setTimeout(doScroll, 50);
                    setTimeout(doScroll, 150);
                    setTimeout(doScroll, 300);
                })();
            </script>
            """,
            height=0,
        )
    
    page_title = page_titles.get(page, "Hevy Data Analyzer")
    current_source = st.session_state["data_source_choice"]
    data_cache = st.session_state["data_cache"]
    raw_hevy_df = data_cache.get(current_source)
    has_data = raw_hevy_df is not None and not raw_hevy_df.empty
    any_data_available = any(
        (df is not None and not df.empty) for df in data_cache.values()
    )
    
    # Use unified title when showing empty state (no data)
    display_title = page_title if has_data else "Hevy Data Analyzer"

    source_options = ["Upload CSV File", "Connect to Hevy API"]
    source_labels = {
        "Upload CSV File": "CSV",
        "Connect to Hevy API": "API",
    }
    source_icons = {
        "Upload CSV File": "📁",
        "Connect to Hevy API": "🔗",
    }

    # Render top title and source summary without an extra container
    if any_data_available:
        title_col, source_col = st.columns([5, 1], gap="large")
    else:
        title_col = st.container()
        source_col = None

    with title_col:
        st.title(display_title)
        header_messages = st.session_state.get("header_messages", [])
        show_all_levels = not has_data
        display_messages = [
            (level, text)
            for level, text in header_messages
            if level == "error" or show_all_levels
        ]
        if display_messages:
            for level, text in display_messages:
                level_class = {
                    "success": "header-alert-success",
                    "warning": "header-alert-warning",
                    "error": "header-alert-error",
                    "info": "header-alert-info",
                }.get(level, "header-alert-info")
                st.markdown(
                    f"<div class='header-alert {level_class}'>{text}</div>",
                    unsafe_allow_html=True,
                )
        st.session_state["header_messages"] = []

    if source_col is not None:
        with source_col:
            meta = st.session_state["data_source_meta"].get(current_source, {})
            sets_summary = meta.get("total_sets")
            workouts_summary = meta.get("workouts_count")
            summary_parts = []
            if sets_summary and workouts_summary:
                summary_parts.append(f"{sets_summary} sets · {workouts_summary} workouts")
            summary_text = " · ".join(summary_parts) if summary_parts else ""
            status_notes = meta.get("status_messages", [])
            # Render summary and notes in a vertically-centered container
            parts_html = ""
            if summary_text:
                parts_html += f"<div style='text-align:right; font-size:0.78rem; color:#8a8f9c;'>{summary_text}</div>"
            for note in status_notes:
                parts_html += f"<div style='text-align:right; font-size:0.75rem; color:#a4b3d1;'>{note}</div>"

            if parts_html:
                st.markdown(
                    f"""
                    <div style='height:100%; display:flex; flex-direction:column; justify-content:center; align-items:flex-end;'>
                        {parts_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    if raw_hevy_df is None or raw_hevy_df.empty:
        render_empty_state()
        return

    # Workouts Review page implementation
    if page == "Workouts Review":
        # Page title and intro intentionally omitted to keep header concise.
        # Keep a visual separator below the page header area.
        st.divider()

        # Prepare data: attach exercise metadata and compute effective metrics
        ex_df = load_exercises()
        processed = prepare_workout_df(raw_hevy_df, ex_df)
        processed = add_effective_metrics(processed)

        # Aggregate per-workout summary (use metric-aware columns so warmups can be included/excluded)
        workout_summary = (
            processed.groupby("workout_id")
            .agg(
                title=("title", "first"),
                start_dt=("start_dt", "first"),
                date=("date", "first"),
                duration_min=("workout_duration_min", "first"),
                volume=("metric_set_volume", "sum"),
                sets=("metric_set_factor", "sum"),
            )
            .reset_index()
            .sort_values("start_dt", ascending=False)
        )

        # The left column provides a filter/search box; skip the redundant top search.
        filtered = workout_summary

        # Make the left column wider (4:6) so the workouts list has more space
        # and the details pane is less wide. Add a 10px spacer column in between.
        left_col, spacer_col, right_col = st.columns([4, 0.3, 6], gap="small")

        with left_col:
            st.markdown("#### Workouts")
            if filtered.empty:
                st.info("No workouts available for the selected data source.")
            else:
                # Build display labels and ensure a stable selection key
                options = filtered["workout_id"].tolist()
                # Simplify long titles: truncate to a reasonable length and append ellipsis
                max_label_title = 36
                labels = [
                    (
                        f"{r.start_dt.strftime('%Y-%m-%d') if pd.notna(r.start_dt) else 'Unknown'} - "
                        + (
                            (r.title[: max_label_title - 1] + "…")
                            if isinstance(r.title, str) and len(r.title) > max_label_title
                            else (r.title or "")
                        )
                    )
                    for r in filtered.itertuples()
                ]
                mapping = dict(zip(options, labels))

                # Allow direct HTML-based list for precise scrollbar/ellipsis behavior.
                # First, check query params so a clicked item can set session state
                # before we fall back to any default selection.
                params = st.query_params
                qp_sel = params.get("selected_workout_id", [None])[0]
                if qp_sel:
                    # URL-decode just in case and compare against both option ids
                    # and the visible labels (mapping values). This handles cases where
                    # the href was built from a label instead of the raw id.
                    qp_decoded = urllib.parse.unquote_plus(str(qp_sel))
                    match = next((o for o in options if str(o) == qp_decoded), None)
                    if match is None:
                        # Try matching against the displayed label
                        match = next((o for o in options if str(mapping.get(o, "")) == qp_decoded), None)
                    if match is None:
                        # Fallback: try to match by title + datetime fragments found in the
                        # decoded query param (handles values like "Title | 2025-12-01 08:02:00").
                        for r in filtered.itertuples():
                            try:
                                title_text = str(r.title or "")
                                start_dt = r.start_dt
                                start_full = start_dt.strftime('%Y-%m-%d %H:%M:%S') if hasattr(start_dt, 'strftime') else str(start_dt)
                                start_short = start_dt.strftime('%Y-%m-%d %H:%M') if hasattr(start_dt, 'strftime') else str(start_dt)
                                date_only = start_dt.strftime('%Y-%m-%d') if hasattr(start_dt, 'strftime') else str(start_dt)
                            except Exception:
                                title_text = str(r.title or "")
                                start_full = start_short = date_only = ""

                            if title_text and title_text in qp_decoded and (
                                (start_full and start_full in qp_decoded) or
                                (start_short and start_short in qp_decoded) or
                                (date_only and date_only in qp_decoded)
                            ):
                                match = r.workout_id
                                break
                    if match is not None:
                        st.session_state["selected_workout_id"] = match

                # Only set a default selection if none exists at all (first load).
                # Do NOT reset selection when the selected workout is not in current
                # filtered/paged options - user wants detail to persist until they
                # explicitly click a new workout.
                if "selected_workout_id" not in st.session_state:
                    st.session_state["selected_workout_id"] = options[0] if options else None

                # Small controls to filter and limit the list for usability
                # Compact search + Clear control (Per page removed; fixed to 10 items/page)
                # Two-column layout: left fills, right fixed 60px, 10px gap
                c1, c2 = st.columns([5, 1], gap="small")
                with c1:
                    filter_q = st.text_input("Filter workouts", key="workouts_list_search", placeholder="Filter by date or title", label_visibility="collapsed")
                with c2:
                    # Use on_click callback to clear safely
                    st.button("Clear", key="workouts_clear", on_click=clear_workouts_filter)

                # If the clear callback requested a rerun, trigger it here (outside
                # the callback). Some Streamlit versions treat rerun calls inside
                # callbacks as a no-op, so we set a flag in the callback and
                # perform the actual rerun at top-level.
                if st.session_state.get("workouts_force_rerun"):
                    try:
                        st.session_state.pop("workouts_force_rerun", None)
                    except Exception:
                        pass
                    try:
                        trigger_rerun()
                    except Exception:
                        pass

                # Pagination: fixed page size (remove Per page selector to simplify UI)
                page_size = 10
                if "workouts_page" not in st.session_state:
                    st.session_state["workouts_page"] = 1

                # Prepare filtered options (fuzzy search: all query words must appear)
                if filter_q:
                    filtered_options = [o for o in options if fuzzy_match(mapping.get(o, "") or str(o), filter_q)]
                else:
                    filtered_options = options[:]

                total_items = len(filtered_options)
                total_pages = max(1, (total_items + page_size - 1) // page_size)

                # Auto-navigate to the page containing the selected workout after Clear
                if st.session_state.get("workouts_navigate_to_selected"):
                    st.session_state.pop("workouts_navigate_to_selected", None)
                    current_sel = st.session_state.get("selected_workout_id")
                    if current_sel and current_sel in filtered_options:
                        sel_idx = filtered_options.index(current_sel)
                        target_page = (sel_idx // page_size) + 1
                        st.session_state["workouts_page"] = target_page
                    else:
                        # If selected workout not in list, go to page 1
                        st.session_state["workouts_page"] = 1

                # Clamp page number
                if st.session_state["workouts_page"] < 1:
                    st.session_state["workouts_page"] = 1
                if st.session_state["workouts_page"] > total_pages:
                    st.session_state["workouts_page"] = total_pages

                start_idx = (st.session_state["workouts_page"] - 1) * page_size
                end_idx = start_idx + page_size
                display_options = filtered_options[start_idx:end_idx]

                # Do NOT reset selection when filtering/paging - let user's previous
                # selection persist in the detail pane until they explicitly click
                # a new workout. Only initialize if there's no selection at all.
                # (The first-load default was already handled above.)

                # Tighter button styling for denser list and a neat card look
                st.markdown(
                    """
                    <style>
                    /* Compact workout list buttons: fixed height, ellipsis, tighter gaps */
                    div.stButton>button{padding:6px 12px; text-align:left; border-radius:8px; width:100% !important; margin-bottom:4px !important; background:#ffffff; border:1px solid #e6e6e6; display:block; align-items:center; min-height:36px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; box-sizing:border-box;}
                    div.stButton>button:hover{background:#fbfdff}
                    div.stButton>button:focus{outline:2px solid rgba(59,130,246,0.25);}

                    /* Workout list items - width 2px shorter than parent */
                    [class*="st-key-workout_btn_"] {
                        width: calc(100% - 2px) !important;
                    }
                    [class*="st-key-workout_btn_"] button {
                        width: 100% !important;
                    }

                    /* Highlight style for selected workout button */
                    [class*="st-key-workout_btn_selected_"] button {
                        background: #e0f2fe !important;
                        border: 2px solid #3b82f6 !important;
                        font-weight: 600 !important;
                    }

                    /* Make Clear, Prev, Next buttons all 60px wide and same height */
                    .st-key-workouts_clear button,
                    .st-key-workouts_prev button,
                    .st-key-workouts_next button {
                        width: 60px !important;
                        min-width: 60px !important;
                        max-width: 60px !important;
                        min-height: 38px !important;
                        padding: 6px 8px !important;
                        text-align: center !important;
                    }
                    /* Align Clear and Next buttons to the right */
                    .st-key-workouts_clear,
                    .st-key-workouts_next {
                        margin-left: auto !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )

                # Pagination controls (Prev / Page X of Y / Next) - use 2 columns like search row
                colp1, colp2 = st.columns([5, 1], gap="small")
                with colp1:
                    # Inner layout for Prev and Page info
                    prev_col, page_col = st.columns([1, 4])
                    with prev_col:
                        if st.button("← Prev", key="workouts_prev"):
                            if st.session_state["workouts_page"] > 1:
                                st.session_state["workouts_page"] -= 1
                                trigger_rerun()
                    with page_col:
                        st.markdown(f"<div style='text-align:center; padding-top:6px;'>Page {st.session_state['workouts_page']} of {total_pages}</div>", unsafe_allow_html=True)
                with colp2:
                    if st.button("Next →", key="workouts_next"):
                        if st.session_state["workouts_page"] < total_pages:
                            st.session_state["workouts_page"] += 1
                            trigger_rerun()

                # Render the compact button list (only the current page items)
                current_sel = st.session_state.get("selected_workout_id")
                with st.container():
                    for i, opt in enumerate(display_options):
                        lbl = mapping.get(opt, opt)
                        # Use "_selected_" in key for highlighted styling when this is the selected workout
                        is_selected = (opt == current_sel)
                        btn_key = f"workout_btn_selected_{start_idx + i}_{opt}" if is_selected else f"workout_btn_{start_idx + i}_{opt}"
                        clicked = st.button(lbl, key=btn_key)
                        if clicked:
                            st.session_state["selected_workout_id"] = opt
                            trigger_rerun()

        with spacer_col:
            # Vertical divider line between workout list and detail pane
            # Use a simple inline style with a large fixed height to ensure visibility
            st.markdown(
                """
                <div style="width: 1px; background-color: #d0d0d0; min-height: 2000px; margin: 0 auto;"></div>
                """,
                unsafe_allow_html=True,
            )

        with right_col:
            sel = st.session_state.get("selected_workout_id")
            if not sel:
                st.info("请选择左侧的某个 workout 以查看动作详情。")
            else:
                wdf = processed[processed["workout_id"] == sel]
                if wdf.empty:
                    st.info("没有找到该 workout 的详细数据。")
                else:
                    title = wdf["title"].iloc[0]
                    start = wdf["start_dt"].iloc[0]

                    # Top header: title + core metrics (Duration / Volume / Records)
                    st.markdown(f"## {title}")
                    st.caption(start.strftime("%Y-%m-%d %H:%M"))

                    duration_min = float(wdf["workout_duration_min"].iloc[0] or 0)
                    hours = int(duration_min // 60)
                    minutes = int(duration_min % 60)
                    duration_str = f"{hours}h {minutes}m" if hours else f"{minutes}m"
                    # Use metric-aware fields so the global "Include Warmup Sets" setting is respected
                    volume_val = convert_volume_for_display(
                        wdf.get("metric_set_volume", wdf.get("set_volume", pd.Series(dtype=float))).sum()
                    )
                    sets_count_raw = float(
                        wdf.get("metric_set_factor", wdf.get("effective_set_factor", pd.Series(dtype=float))).sum()
                    )
                    records_count = int(round(sets_count_raw))

                    # Metrics row (styled similarly to Home Workout Log)
                    mcol1, mcol2, mcol3 = st.columns([1,1,1])
                    with mcol1:
                        st.markdown("<div style='color:#6b7280; font-size:0.85rem;'>Duration</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-weight:700; font-size:1.15rem;'>{duration_str}</div>", unsafe_allow_html=True)
                    with mcol2:
                        st.markdown("<div style='color:#6b7280; font-size:0.85rem;'>Volume</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-weight:700; font-size:1.15rem;'>{int(volume_val):,} {get_weight_unit_suffix()}</div>", unsafe_allow_html=True)
                    with mcol3:
                        st.markdown("<div style='color:#6b7280; font-size:0.85rem;'>Sets</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='font-weight:700; font-size:1.15rem;'>{records_count}</div>", unsafe_allow_html=True)

                    st.markdown("<hr style='margin:12px 0'>", unsafe_allow_html=True)

                    # Add CSS to style exercise title buttons as links
                    st.markdown("""
                    <style>
                    /* Style exercise title buttons as links */
                    [class*="st-key-ex_link_"] button {
                        background: transparent !important;
                        border: none !important;
                        color: #1e40af !important;
                        font-weight: 700 !important;
                        font-size: 1.35rem !important;
                        padding: 0 !important;
                        text-align: left !important;
                        cursor: pointer !important;
                        min-height: 0 !important;
                        line-height: 1.3 !important;
                    }
                    [class*="st-key-ex_link_"] button p {
                        font-weight: 700 !important;
                        font-size: 1.35rem !important;
                        margin: 0 !important;
                    }
                    [class*="st-key-ex_link_"] button:hover {
                        text-decoration: underline !important;
                        color: #1e3a8a !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    # Exercises breakdown with media and per-set badges
                    # Determine exercise order strictly as they appear in the API/raw data
                    # Preserve original appearance order in `wdf` and keep the first occurrence
                    exercise_order = list(wdf["exercise_title"].drop_duplicates())

                    # Precompute per-exercise aggregates (metric-aware)
                    ex_summary = (
                        wdf.groupby("exercise_title")
                        .agg(sets=("metric_set_factor", "sum"), volume=("metric_set_volume", "sum"))
                        .reset_index()
                    )

                    # Compute longest exercise title across the loaded dataset so we can
                    # size the title container to avoid truncation/ellipsis.
                    try:
                        max_title_len = int(processed["exercise_title"].dropna().astype(str).map(len).max())
                    except Exception:
                        max_title_len = 40
                    # Clamp to reasonable bounds to avoid layout blowouts
                    max_title_len = max(20, min(max_title_len, 100))

                    for ex_title in exercise_order:
                        ex = ex_summary[ex_summary["exercise_title"] == ex_title].iloc[0]
                        ex_rows = wdf[wdf["exercise_title"] == ex_title]
                        # pick first media_url / exercise_type / format from merged exercise metadata
                        media_url = ex_rows["media_url"].dropna().astype(str)
                        media_url = media_url.iloc[0] if not media_url.empty and media_url.iloc[0] != "" else None
                        ex_type = ex_rows["exercise_type"].dropna().astype(str)
                        ex_type = ex_type.iloc[0] if not ex_type.empty and ex_type.iloc[0] != "" else ""
                        ex_format = ex_rows["format"].dropna().astype(str)
                        ex_format = ex_format.iloc[0] if not ex_format.empty and ex_format.iloc[0] != "" else ""

                        # Precompute per-exercise subtotal values so we can render them in the right column
                        try:
                            ex_volume_raw = ex_rows.get("metric_set_volume", ex_rows.get("set_volume", pd.Series(dtype=float))).sum()
                        except Exception:
                            ex_volume_raw = 0.0
                        ex_volume_disp = convert_volume_for_display(float(ex_volume_raw or 0.0))
                        ex_volume_unit = get_weight_unit_suffix()
                        ex_sets_count = ex_rows.get("metric_set_factor", ex_rows.get("effective_set_factor", pd.Series(dtype=float))).sum()

                        # Note: per-set header badges are rendered below; subtotal (Volume/Sets)
                        # will be rendered under the exercise title above the set list.

                        # Prepare subtotal HTML (will be placed under the exercise title)
                        subtotal_html = (
                            "<div style='margin-top:6px; display:flex; gap:18px; align-items:center; justify-content:flex-start;'>"
                            "<div style='display:flex; flex-direction:column; align-items:flex-start; white-space:nowrap;'>"
                            "<div style='color:#6b7280; font-size:0.75rem;'>Volume</div>"
                            f"<div style='font-weight:700; font-size:1.05rem; white-space:nowrap;'>{ex_volume_disp:.1f} {ex_volume_unit}</div>"
                            "</div>"
                            "<div style='display:flex; flex-direction:column; align-items:flex-start; white-space:nowrap;'>"
                            "<div style='color:#6b7280; font-size:0.75rem;'>Sets</div>"
                            f"<div style='font-weight:700; font-size:1.05rem; white-space:nowrap;'>{int(round(ex_sets_count))}</div>"
                            "</div>"
                            "</div>"
                        )

                        # Render two columns below the header: title/info and a small stat column.
                        # The media column has been removed so subsequent elements shift left.
                        col_info, col_stat = st.columns([4.6, 1.4])
                        with col_info:
                            # Render exercise title as a clickable button that navigates to Exercise Review
                            # Use a unique key for each exercise button within this workout
                            ex_btn_key = f"ex_link_{sel}_{ex_title}"
                            if st.button(ex_title, key=ex_btn_key, type="tertiary"):
                                st.session_state["selected_exercise"] = ex_title
                                st.session_state["nav_page"] = "Exercise Review"
                                st.rerun()
                        with col_stat:
                            # Right stat intentionally left blank — subtotal (Volume/Sets) is shown next to the title.
                            st.markdown("", unsafe_allow_html=True)

                        # Per-set list with badges
                        # Ensure sets are ordered: prefer set_index when it represents appearance order,
                        # otherwise preserve the appearance order in `ex_rows` (which comes from processed)
                        # Render header badges aligned with per-set badges (shows 'Set' and exercise_type)
                        # Style: black text, no border, aligned vertically with the numeric badges below
                        ex_type_display = str(ex_type).strip() if ex_type else ""
                        # Match per-set row left padding so header text lines up with record column
                        # Use smaller vertical padding for a denser layout
                        header_combined_html = "<div style='padding:6px 12px; margin-bottom:4px; line-height:1; display:flex; align-items:center;'>"
                        # Use distinct fixed widths so header 'Set' and the exercise-type badge
                        # can have different sizes (Set smaller, exercise type wider).
                        badge_width_set = 56
                        badge_width_type = 200
                        badge_width_per = 30
                        badge_margin = 16
                        # Padding used inside the exercise-type header span
                        header_padding_left = 20
                        header_combined_html += (
                            f"<span style='display:inline-block; vertical-align:middle; width:{badge_width_set}px; padding:4px 6px; border-radius:6px; "
                            f"background:transparent; color:#000; font-weight:700; margin-right:{badge_margin}px; text-align:center; border:none; line-height:1;'>Set</span>"
                        )
                        if ex_type_display:
                            # Left-align the exercise-type text and add slight left padding
                            header_combined_html += (
                                f"<span style='display:inline-block; vertical-align:middle; width:{badge_width_type}px; padding:6px 8px; padding-left:{header_padding_left}px; border-radius:6px; background:transparent; color:#000; font-weight:700; text-align:left; line-height:1;'>{ex_type_display}</span>"
                            )
                        header_combined_html += "</div>"
                        st.markdown(header_combined_html, unsafe_allow_html=True)
                        if "set_index" in ex_rows.columns and ex_rows["set_index"].notna().any():
                            sets_df = ex_rows.sort_values("set_index").copy()
                        else:
                            sets_df = ex_rows.copy()

                        # Build numbering for formal sets: exclude warmups and drop-sets from numbering
                        st_types = sets_df["set_type"].fillna("").astype(str).str.lower()
                        is_warm = st_types.str.contains("warm")
                        is_drop = st_types.str.contains("drop") | st_types.str.contains("dropset") | st_types.str.contains("drop-set")

                        # Rows that should receive numeric sequence (formal sets): not warm and not drop
                        numbered_mask = ~(is_warm | is_drop)
                        numbered_indices = sets_df[numbered_mask].index.tolist()
                        numbered_map = {idx: i + 1 for i, idx in enumerate(numbered_indices)}

                        # For formatting, prefer explicit raw columns: weight_kg, weight_lbs, reps, distance_km, distance_miles, duration_seconds
                        ex_format_local = str(ex_rows["format"].dropna().astype(str).iloc[0]) if ex_rows["format"].dropna().any() else ""
                        unit = get_weight_unit_suffix()

                        # Render sets with alternating background colors (striped rows)
                        row_i = 0
                        for idx, s in sets_df.iterrows():
                            st_type = str(s.get("set_type", "")).lower() if s.get("set_type") is not None else ""
                            badge = ""
                            badge_color = "#e2e8f0"
                            if "warm" in st_type:
                                badge = "W"
                                badge_color = "#fef3c7"
                            elif "drop" in st_type or "dropset" in st_type or "drop-set" in st_type:
                                badge = "D"
                                badge_color = "#ede9fe"
                            else:
                                # Use sequential numbering for formal sets (start at 1 after removing warmups)
                                if idx in numbered_map:
                                    badge = str(numbered_map[idx])
                                else:
                                    # fallback to set_index if somehow missing
                                    idx_val = s.get("set_index")
                                    if pd.notna(idx_val):
                                        try:
                                            badge = str(int(idx_val))
                                        except Exception:
                                            badge = "1"
                                    else:
                                        badge = "1"

                            # Format set record according to exercise format/type
                            record_text = ""

                            # Treat Stretching explicitly as duration-based
                            if (ex_type and str(ex_type).strip().lower() == "stretching") or ex_format_local.upper() == "TIME" or ex_format_local.upper() == "DURATION":
                                # Use duration_seconds if available
                                dur = s.get("duration_seconds") if "duration_seconds" in s.index else None
                                if pd.notna(dur) and dur:
                                    try:
                                        ds = int(dur)
                                        mins = ds // 60
                                        secs = ds % 60
                                        record_text = f"{mins}m {secs}s"
                                    except Exception:
                                        record_text = str(dur)
                                else:
                                    record_text = "-"
                            elif ex_format_local.upper() in ("DISTANCE & DURATION", "DISTANCE"):
                                # distance (prefer distance_km or distance_miles)
                                if "distance_km" in s.index and pd.notna(s.get("distance_km")):
                                    record_text = f"{float(s.get('distance_km')):.2f} {get_distance_unit_suffix()}"
                                elif "distance_miles" in s.index and pd.notna(s.get("distance_miles")):
                                    record_text = f"{float(s.get('distance_miles')):.2f} MI"
                                else:
                                    record_text = "-"
                            else:
                                # Default: weight & reps style. Prefer weight_kg, then adjusted_weight, then weight_lbs (convert), then weight
                                weight_val = None
                                if "weight_kg" in s.index and pd.notna(s.get("weight_kg")):
                                    weight_val = float(s.get("weight_kg"))
                                elif "adjusted_weight" in s.index and pd.notna(s.get("adjusted_weight")):
                                    weight_val = float(s.get("adjusted_weight"))
                                elif "weight_lbs" in s.index and pd.notna(s.get("weight_lbs")):
                                    try:
                                        weight_val = float(s.get("weight_lbs")) * 0.45359237
                                    except Exception:
                                        weight_val = None
                                elif "weight" in s.index and pd.notna(s.get("weight")):
                                    try:
                                        weight_val = float(s.get("weight"))
                                    except Exception:
                                        weight_val = None

                                reps = int(s.get("reps", 0) or 0)
                                if weight_val is None:
                                    weight_val = 0.0
                                weight_disp = convert_weight_for_display(weight_val)
                                record_text = f"{weight_disp:.1f} {unit} × {reps} reps"

                            # Ensure per-set badges use the same fixed width and margin as the header badge
                            # Wrap the small per-set badge inside a fixed-width container equal to the header 'Set' width
                            # so the small badge is centered under the header text. The outer container carries the
                            # right margin to match header spacing.
                            badge_html = (
                                f"<span style='display:inline-block; vertical-align:middle; width:{badge_width_set}px; text-align:center; margin-right:{badge_margin}px;'>"
                                f"<span style='display:inline-block; vertical-align:middle; width:{badge_width_per}px; padding:4px 6px; border-radius:6px; background:{badge_color}; font-weight:700; text-align:center; line-height:1;'>{badge}</span>"
                                f"</span>"
                            )
                            # Spacer should equal the header's inner left padding so the record column aligns
                            spacer_px = header_padding_left
                            spacer_html = f"<span style='display:inline-block; width:{spacer_px}px;'></span>"
                            # Determine row background for zebra striping
                            bg = "#ffffff" if (row_i % 2 == 0) else "#f3f4f6"
                            # Build a compact row with padding so the stripe is visible (matches screenshot feel)
                            set_row_html = (
                                f"<div style='background:{bg}; padding:6px 10px; border-radius:6px; margin-bottom:6px; display:flex; align-items:center;'>"
                                f"{badge_html}{spacer_html}<div style='flex:1; font-size:0.98rem; color:#111;'>{record_text}</div>"
                                "</div>"
                            )
                            st.markdown(set_row_html, unsafe_allow_html=True)
                            row_i += 1
                        # Add a subtle divider between exercises (but not after the last one)
                        try:
                            if exercise_order.index(ex_title) != len(exercise_order) - 1:
                                st.markdown("<hr style='margin:12px 0; border:none; border-top:1px solid #e5e7eb;'>", unsafe_allow_html=True)
                        except Exception:
                            # Fallback spacer if anything goes wrong locating index
                            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # Exercise Review page implementation
    if page == "Exercise Review":
        st.divider()
        
        # Check for unconfigured custom exercises and show warning at the top
        unconfigured_exercises = get_unconfigured_custom_exercises(raw_hevy_df)
        if unconfigured_exercises:
            count = len(unconfigured_exercises)
            exercise_list = ", ".join(unconfigured_exercises[:3])
            if count > 3:
                exercise_list += f" ... (+{count - 3} more)"
            if st.button(
                f"⚠️ {count} custom exercise(s) not configured: {exercise_list}. Click to configure.",
                key="exercise_review_unconfigured_warning",
                type="tertiary",
            ):
                st.session_state["nav_page"] = "Settings"
                st.rerun()

        # Prepare data
        ex_df = load_exercises()
        processed = prepare_workout_df(raw_hevy_df, ex_df)
        processed = add_effective_metrics(processed)

        # Ensure required columns exist in ex_df
        if "equipment" not in ex_df.columns:
            ex_df["equipment"] = ""
        if "primary_muscle" not in ex_df.columns:
            ex_df["primary_muscle"] = ""
        if "other_muscles" not in ex_df.columns:
            ex_df["other_muscles"] = ""
        if "media_url" not in ex_df.columns:
            ex_df["media_url"] = ""

        # Ensure date column is datetime for proper aggregation
        processed = processed.copy()
        processed["date"] = pd.to_datetime(processed["date"], errors="coerce")

        # Build exercise summary: aggregate stats per exercise
        exercise_summary = (
            processed.groupby("exercise_title")
            .agg(
                total_sets=("metric_set_factor", "sum"),
                total_volume=("metric_set_volume", "sum"),
                workout_count=("workout_id", "nunique"),
                first_date=("date", "min"),
                last_date=("date", "max"),
            )
            .reset_index()
            .sort_values("total_sets", ascending=False)
        )

        # Reload exercises fresh using load_exercises() which merges custom_exercises.csv
        # This ensures we have the latest equipment/muscle data including user customizations
        fresh_ex_df = load_exercises()
        fresh_ex_df["exercise_title"] = fresh_ex_df["exercise_title"].astype(str).str.strip()
        
        # Ensure required columns exist
        if "equipment" not in fresh_ex_df.columns:
            fresh_ex_df["equipment"] = ""
        if "primary_muscle" not in fresh_ex_df.columns:
            fresh_ex_df["primary_muscle"] = ""
        if "other_muscles" not in fresh_ex_df.columns:
            fresh_ex_df["other_muscles"] = ""
        if "media_url" not in fresh_ex_df.columns:
            fresh_ex_df["media_url"] = ""
        
        # Fill NaN values
        fresh_ex_df["equipment"] = fresh_ex_df["equipment"].fillna("")
        fresh_ex_df["primary_muscle"] = fresh_ex_df["primary_muscle"].fillna("")
        fresh_ex_df["other_muscles"] = fresh_ex_df["other_muscles"].fillna("")
        fresh_ex_df["media_url"] = fresh_ex_df["media_url"].fillna("")

        # Ensure exercise_title is stripped in exercise_summary
        exercise_summary["exercise_title"] = exercise_summary["exercise_title"].astype(str).str.strip()

        # Merge exercise metadata (equipment, primary_muscle, etc.) from fresh CSV
        exercise_summary = exercise_summary.merge(
            fresh_ex_df[["exercise_title", "equipment", "primary_muscle", "other_muscles", "media_url"]].drop_duplicates("exercise_title"),
            on="exercise_title",
            how="left",
        )
        
        # Fill NaN values after merge
        exercise_summary["equipment"] = exercise_summary["equipment"].fillna("")
        exercise_summary["primary_muscle"] = exercise_summary["primary_muscle"].fillna("")
        exercise_summary["other_muscles"] = exercise_summary["other_muscles"].fillna("")
        exercise_summary["media_url"] = exercise_summary["media_url"].fillna("")

        # Identify custom exercises (in user data but not in exercises.csv)
        csv_exercise_titles = set(fresh_ex_df["exercise_title"].unique())
        user_exercise_titles = set(exercise_summary["exercise_title"].unique())
        custom_exercise_titles = user_exercise_titles - csv_exercise_titles

        # Create full exercise list from exercises.csv (all exercises, not just user's)
        all_exercises = fresh_ex_df[["exercise_title", "equipment", "primary_muscle", "other_muscles", "media_url"]].drop_duplicates("exercise_title").copy()
        
        # Add custom exercises to the list
        custom_exercises_df = exercise_summary[exercise_summary["exercise_title"].isin(custom_exercise_titles)][
            ["exercise_title", "equipment", "primary_muscle", "other_muscles", "media_url"]
        ].copy()
        all_exercises = pd.concat([all_exercises, custom_exercises_df], ignore_index=True).drop_duplicates("exercise_title")
        
        # Mark which exercises are custom (editable)
        all_exercises["is_custom"] = all_exercises["exercise_title"].isin(custom_exercise_titles)
        
        # Merge user's stats into all exercises (left join to keep all exercises)
        all_exercises = all_exercises.merge(
            exercise_summary[["exercise_title", "total_sets", "total_volume", "workout_count", "first_date", "last_date"]],
            on="exercise_title",
            how="left",
        )
        
        # Fill NaN for exercises without user data
        all_exercises["total_sets"] = all_exercises["total_sets"].fillna(0)
        all_exercises["total_volume"] = all_exercises["total_volume"].fillna(0)
        all_exercises["workout_count"] = all_exercises["workout_count"].fillna(0)
        
        # Sort: exercises with user data first (by total_sets desc), then alphabetically
        all_exercises["has_data"] = all_exercises["total_sets"] > 0
        all_exercises = all_exercises.sort_values(
            ["has_data", "total_sets", "exercise_title"],
            ascending=[False, False, True]
        )

        # Get unique equipment and muscles for filters from ALL exercises in CSV
        all_equipment = set(all_exercises["equipment"].unique().tolist())
        # Separate "None" (no equipment needed) from empty/blank (not set)
        has_none = "None" in all_equipment or any(str(e) == "None" for e in all_equipment)
        # Filter out empty strings and None type, but keep "None" string
        equipment_list = [e for e in all_equipment if e and str(e).strip() and str(e) != "None"]
        equipment_list = sorted([e for e in equipment_list if e != "Other"])
        if "Other" in all_equipment:
            equipment_list.append("Other")
        # Add "None" at the beginning (right after "All Equipment")
        if has_none:
            equipment_list = ["None"] + equipment_list
        
        all_muscles = set(all_exercises["primary_muscle"].unique().tolist())
        muscles_list = [m for m in all_muscles if m and m.strip()]
        muscles_list = sorted([m for m in muscles_list if m != "Other"])
        if "Other" in all_muscles:
            muscles_list.append("Other")

        # Left/right column layout with spacer
        left_col, spacer_col, right_col = st.columns([4, 0.3, 6], gap="small")

        with left_col:
            # Header row with title and Custom Exercises toggle
            custom_count = len(custom_exercise_titles)
            
            # Style for the toggle button - align to right
            toggle_style = """
            <style>
            /* Target the stVerticalBlock that directly contains the toggle button element */
            .stVerticalBlock:has(> .stElementContainer.st-key-custom_exercises_toggle) {
                align-items: flex-end !important;
            }
            .st-key-custom_exercises_toggle button {
                font-size: 0.75rem !important;
                padding: 4px 10px !important;
                min-height: 32px !important;
                white-space: nowrap !important;
            }
            </style>
            """
            st.markdown(toggle_style, unsafe_allow_html=True)
            
            header_col1, header_col2 = st.columns([3, 2])
            with header_col1:
                st.markdown("#### Exercises")
            with header_col2:
                # Custom Exercises toggle button
                if custom_count > 0:
                    # Initialize session state
                    if "show_custom_only" not in st.session_state:
                        st.session_state["show_custom_only"] = False
                    
                    btn_label = f"✏️ Custom ({custom_count})" if st.session_state["show_custom_only"] else f"Custom ({custom_count})"
                    if st.button(btn_label, key="custom_exercises_toggle", type="primary" if st.session_state["show_custom_only"] else "secondary"):
                        st.session_state["show_custom_only"] = not st.session_state["show_custom_only"]
                        # Navigate to the page containing the selected exercise
                        st.session_state["exercises_navigate_to_selected"] = True
                        trigger_rerun()

            # Search box, filters, and Clear button layout
            # Left side: search box on top, two filter dropdowns below
            # Right side: Clear button spanning both rows
            filter_left_col, filter_right_col = st.columns([5, 1], gap="small")
            
            with filter_left_col:
                # Search box
                exercise_search_q = st.text_input(
                    "Filter exercises",
                    key="exercises_list_search",
                    placeholder="Filter by name",
                    label_visibility="collapsed"
                )
                # Two filter dropdowns side by side
                filter_col1, filter_col2 = st.columns(2)
                with filter_col1:
                    selected_equipment = st.selectbox(
                        "Equipment",
                        options=["All Equipment"] + equipment_list,
                        key="exercise_filter_equipment",
                        label_visibility="collapsed",
                    )
                with filter_col2:
                    selected_muscle = st.selectbox(
                        "Muscle",
                        options=["All Muscles"] + muscles_list,
                        key="exercise_filter_muscle",
                        label_visibility="collapsed",
                    )
            
            with filter_right_col:
                # Clear button spanning full height (two rows) - 95px to align with search box top and filter bottom
                st.markdown(
                    """
                    <style>
                    /* Target the right column's vertical block to remove gap and align to top */
                    .st-emotion-cache-hh1p47 .stVerticalBlock {
                        gap: 0 !important;
                        justify-content: flex-start !important;
                    }
                    /* Hide the style element container to avoid taking space */
                    .st-emotion-cache-hh1p47 .stVerticalBlock > .stElementContainer:has(.stMarkdown) {
                        display: none !important;
                    }
                    .st-key-exercises_clear {
                        height: auto !important;
                        display: flex !important;
                        align-items: flex-start !important;
                    }
                    .st-key-exercises_clear > div {
                        height: auto !important;
                    }
                    .st-key-exercises_clear button {
                        width: 60px !important;
                        min-width: 60px !important;
                        max-width: 60px !important;
                        height: 95px !important;
                        min-height: 95px !important;
                        max-height: 95px !important;
                        padding: 6px 8px !important;
                        text-align: center !important;
                        white-space: nowrap !important;
                        overflow: hidden !important;
                        margin-top: 0 !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
                st.button("Clear", key="exercises_clear", on_click=clear_exercises_filter)
            
            # Handle rerun flag from clear callback
            if st.session_state.get("exercises_force_rerun"):
                try:
                    st.session_state.pop("exercises_force_rerun", None)
                except Exception:
                    pass
                try:
                    trigger_rerun()
                except Exception:
                    pass

            # Detect filter changes and reset to page 1 if filters changed
            current_filters = (
                exercise_search_q or "",
                selected_equipment,
                selected_muscle,
                st.session_state.get("show_custom_only", False)
            )
            prev_filters = st.session_state.get("exercises_prev_filters", None)
            if prev_filters is not None and current_filters != prev_filters:
                # Filters changed, reset to page 1
                st.session_state["exercises_page"] = 1
            st.session_state["exercises_prev_filters"] = current_filters

            # Apply filters
            filtered_exercises = all_exercises.copy()
            
            # Apply search filter first (fuzzy search: all query words must appear)
            if exercise_search_q:
                filtered_exercises = filtered_exercises[
                    filtered_exercises["exercise_title"].apply(lambda x: fuzzy_match(x, exercise_search_q))
                ]
            
            # Apply Custom Exercises filter if enabled
            if st.session_state.get("show_custom_only", False):
                filtered_exercises = filtered_exercises[filtered_exercises["is_custom"] == True]
            
            if selected_equipment != "All Equipment":
                filtered_exercises = filtered_exercises[filtered_exercises["equipment"] == selected_equipment]
            if selected_muscle != "All Muscles":
                filtered_exercises = filtered_exercises[filtered_exercises["primary_muscle"] == selected_muscle]

            if filtered_exercises.empty:
                st.info("No exercises match the selected filters.")
            else:
                # Build display labels
                options = filtered_exercises["exercise_title"].tolist()
                max_label_title = 36
                labels = [
                    (title[:max_label_title - 1] + "…") if len(title) > max_label_title else title
                    for title in options
                ]
                mapping = dict(zip(options, labels))

                # Initialize selection
                if "selected_exercise" not in st.session_state:
                    st.session_state["selected_exercise"] = options[0] if options else None

                # Pagination
                page_size = 10
                if "exercises_page" not in st.session_state:
                    st.session_state["exercises_page"] = 1

                total_items = len(options)
                total_pages = max(1, (total_items + page_size - 1) // page_size)

                # Auto-navigate to the page containing the selected exercise after Clear
                if st.session_state.get("exercises_navigate_to_selected"):
                    st.session_state.pop("exercises_navigate_to_selected", None)
                    current_sel = st.session_state.get("selected_exercise")
                    if current_sel and current_sel in options:
                        sel_idx = options.index(current_sel)
                        target_page = (sel_idx // page_size) + 1
                        st.session_state["exercises_page"] = target_page
                    else:
                        # If selected exercise not in list, go to page 1
                        st.session_state["exercises_page"] = 1

                # Clamp page number
                if st.session_state["exercises_page"] < 1:
                    st.session_state["exercises_page"] = 1
                if st.session_state["exercises_page"] > total_pages:
                    st.session_state["exercises_page"] = total_pages

                start_idx = (st.session_state["exercises_page"] - 1) * page_size
                end_idx = start_idx + page_size
                display_options = options[start_idx:end_idx]

                # Styling for exercise list buttons (matching Workouts Review style)
                st.markdown(
                    """
                    <style>
                    /* Exercise list items - width 2px shorter than parent (matching workout list) */
                    [class*="st-key-exercise_btn_"] {
                        width: calc(100% - 2px) !important;
                    }
                    [class*="st-key-exercise_btn_"] button {
                        width: 100% !important;
                        text-align: left !important;
                        justify-content: flex-start !important;
                    }
                    [class*="st-key-exercise_btn_"] button p {
                        text-align: left !important;
                    }

                    /* Highlight selected exercise */
                    [class*="st-key-exercise_btn_selected_"] button {
                        background: #e0f2fe !important;
                        border: 2px solid #3b82f6 !important;
                        font-weight: 600 !important;
                    }

                    /* Prev, Next buttons */
                    .st-key-exercises_prev button,
                    .st-key-exercises_next button {
                        width: 60px !important;
                        min-width: 60px !important;
                        max-width: 60px !important;
                        min-height: 38px !important;
                        padding: 6px 8px !important;
                        text-align: center !important;
                        white-space: nowrap !important;
                        overflow: hidden !important;
                    }
                    .st-key-exercises_next {
                        margin-left: auto !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )

                # Pagination controls
                colp1, colp2, colp3 = st.columns([1, 2, 1])
                with colp1:
                    if st.button("← Prev", key="exercises_prev"):
                        if st.session_state["exercises_page"] > 1:
                            st.session_state["exercises_page"] -= 1
                            trigger_rerun()
                with colp2:
                    st.markdown(
                        f"<div style='text-align:center; padding-top:6px;'>Page {st.session_state['exercises_page']} of {total_pages}</div>",
                        unsafe_allow_html=True,
                    )
                with colp3:
                    if st.button("Next →", key="exercises_next"):
                        if st.session_state["exercises_page"] < total_pages:
                            st.session_state["exercises_page"] += 1
                            trigger_rerun()

                # Render exercise list
                current_sel = st.session_state.get("selected_exercise")
                with st.container():
                    for i, opt in enumerate(display_options):
                        lbl = mapping.get(opt, opt)
                        is_selected = (opt == current_sel)
                        btn_key = f"exercise_btn_selected_{start_idx + i}_{opt}" if is_selected else f"exercise_btn_{start_idx + i}_{opt}"
                        clicked = st.button(lbl, key=btn_key)
                        if clicked:
                            st.session_state["selected_exercise"] = opt
                            trigger_rerun()

        with spacer_col:
            # Vertical divider
            st.markdown(
                '<div style="width: 1px; background-color: #d0d0d0; min-height: 2000px; margin: 0 auto;"></div>',
                unsafe_allow_html=True,
            )

        with right_col:
            sel_exercise = st.session_state.get("selected_exercise")
            if not sel_exercise:
                st.info("请选择左侧的某个动作以查看详情。")
            else:
                # Check if this is a custom exercise (editable)
                is_custom_exercise = sel_exercise in custom_exercise_titles
                
                # Get exercise metadata from fresh_ex_df (all exercises from CSV)
                ex_meta = fresh_ex_df[fresh_ex_df["exercise_title"] == sel_exercise]
                
                # For custom exercises, first check saved file, then session state
                if is_custom_exercise:
                    # Load from persisted custom exercises file first
                    saved_custom = get_custom_exercise_metadata(sel_exercise)
                    ex_equipment = saved_custom.get("equipment", "")
                    ex_muscle = saved_custom.get("primary_muscle", "")
                    ex_other_muscles = saved_custom.get("secondary_muscles", "")
                    ex_media_url = None
                elif ex_meta.empty:
                    ex_equipment = ""
                    ex_muscle = ""
                    ex_other_muscles = ""
                    ex_media_url = None
                else:
                    ex_equipment = ex_meta["equipment"].iloc[0] or ""
                    ex_muscle = ex_meta["primary_muscle"].iloc[0] or ""
                    ex_other_muscles = ex_meta["other_muscles"].iloc[0] or ""
                    ex_media_url = ex_meta["media_url"].iloc[0] if "media_url" in ex_meta.columns else None

                # Get exercise_type from metadata
                if not ex_meta.empty and "exercise_type" in ex_meta.columns:
                    ex_type = ex_meta["exercise_type"].iloc[0] or "Weight & Reps"
                else:
                    ex_type = "Weight & Reps"  # Default type

                # Get all sets for this exercise
                ex_data_all = processed[processed["exercise_title"] == sel_exercise].copy()
                
                # Filter warmup sets for stats calculations if setting is disabled
                include_warmups = bool(st.session_state.get("include_warmup_sets", False))
                if include_warmups:
                    ex_data = ex_data_all.copy()
                else:
                    # Exclude warmup sets for statistics
                    if "set_type" in ex_data_all.columns:
                        ex_data = ex_data_all[~ex_data_all["set_type"].fillna("").astype(str).str.lower().str.contains("warm")].copy()
                    else:
                        ex_data = ex_data_all.copy()

                # Create tabs - remove Edit tab, editing is now inline in Summary
                tab1, tab2 = st.tabs(["📊 Summary", "📅 History"])

                with tab1:
                    # Exercise header
                    st.markdown(f"## {sel_exercise}")
                    if is_custom_exercise:
                        st.caption("✏️ Custom Exercise (editable)")
                    
                    # For custom exercises, show editable dropdowns; for standard exercises, show static text
                    if is_custom_exercise:
                        # Build equipment options: None first, then sorted list, empty string as "Not Set"
                        equip_options = ["Not Set", "None"] + sorted([e for e in equipment_list if e and e != "None"])
                        current_equip = ex_equipment if ex_equipment else "Not Set"
                        if current_equip not in equip_options:
                            equip_options.append(current_equip)
                        
                        # Build muscle options - "Not Set" for unconfigured, "None" for explicitly no muscle
                        muscle_options = ["Not Set", "None"] + sorted([m for m in muscles_list if m])
                        current_muscle = ex_muscle if ex_muscle else "Not Set"
                        if current_muscle not in muscle_options:
                            muscle_options.append(current_muscle)
                        
                        # Compact CSS for inline label + dropdown layout
                        st.markdown("""<style>
/* Hide labels for custom exercise dropdowns */
.st-key-custom_ex_equipment label, .st-key-custom_ex_primary label, .st-key-custom_ex_secondary label {
    display: none !important;
}
/* Reduce bottom margin */
.st-key-custom_ex_equipment, .st-key-custom_ex_primary, .st-key-custom_ex_secondary {
    margin-bottom: 0.25rem !important;
}
/* Label containers and all parent elements - vertically center */
.st-key-eq_label_col,
.st-key-pm_label_col,
.st-key-sm_label_col {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    min-height: 38px !important;
}
/* Inner vertical block inside label container */
.st-key-eq_label_col > div.stVerticalBlock,
.st-key-pm_label_col > div.stVerticalBlock,
.st-key-sm_label_col > div.stVerticalBlock {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: 0 !important;
}
/* Element container inside */
.st-key-eq_label_col .stElementContainer,
.st-key-pm_label_col .stElementContainer,
.st-key-sm_label_col .stElementContainer {
    display: flex !important;
    align-items: center !important;
}
/* Markdown container */
.st-key-eq_label_col .stMarkdown,
.st-key-pm_label_col .stMarkdown,
.st-key-sm_label_col .stMarkdown {
    display: flex !important;
    align-items: center !important;
    margin: 0 !important;
}
/* Text paragraph */
.st-key-eq_label_col .stMarkdown p,
.st-key-pm_label_col .stMarkdown p,
.st-key-sm_label_col .stMarkdown p {
    margin: 0 !important;
    line-height: 38px !important;
}
</style>""", unsafe_allow_html=True)
                        
                        # Equipment row: label + dropdown
                        eq_col1, eq_col2 = st.columns([2, 3])
                        with eq_col1:
                            with st.container(key="eq_label_col"):
                                st.markdown("**Equipment**")
                        with eq_col2:
                            new_equipment = st.selectbox(
                                "Equipment",
                                options=equip_options,
                                index=equip_options.index(current_equip) if current_equip in equip_options else 0,
                                key="custom_ex_equipment",
                                label_visibility="collapsed",
                            )
                        
                        # Primary Muscle Group row: label + dropdown
                        pm_col1, pm_col2 = st.columns([2, 3])
                        with pm_col1:
                            with st.container(key="pm_label_col"):
                                st.markdown("**Primary Muscle Group**")
                        with pm_col2:
                            new_primary = st.selectbox(
                                "Primary Muscle Group",
                                options=muscle_options,
                                index=muscle_options.index(current_muscle) if current_muscle in muscle_options else 0,
                                key="custom_ex_primary",
                                label_visibility="collapsed",
                            )
                        
                        # Secondary Muscle Group - multiselect dropdown
                        # Parse current secondary muscles (separated by ; or ,)
                        current_secondary = ex_other_muscles if ex_other_muscles else ""
                        current_secondary_list = [m.strip() for m in current_secondary.replace(",", ";").split(";") if m.strip()]
                        
                        # Build options for secondary muscles (exclude "None", include all muscles)
                        secondary_options = sorted([m for m in muscles_list if m])
                        
                        # Ensure current values are in options
                        for m in current_secondary_list:
                            if m and m not in secondary_options:
                                secondary_options.append(m)
                        secondary_options = sorted(secondary_options)
                        
                        # Check if Primary Muscle is None or Not Set - if so, disable Secondary
                        primary_is_none = (new_primary in ["None", "Not Set"])
                        
                        # Secondary Muscle Group row: label + multiselect
                        sm_col1, sm_col2 = st.columns([2, 3])
                        with sm_col1:
                            with st.container(key="sm_label_col"):
                                st.markdown("**Secondary Muscle Group**")
                        with sm_col2:
                            if primary_is_none:
                                # Show disabled placeholder when Primary is None
                                st.selectbox(
                                    "Secondary Muscle Group",
                                    options=["None"],
                                    index=0,
                                    key="custom_ex_secondary_disabled",
                                    disabled=True,
                                    label_visibility="collapsed",
                                )
                                new_secondary_list = []
                            else:
                                new_secondary_list = st.multiselect(
                                    "Secondary Muscle Group",
                                    options=secondary_options,
                                    default=[m for m in current_secondary_list if m in secondary_options],
                                    key="custom_ex_secondary",
                                    placeholder="Select (optional)",
                                    label_visibility="collapsed",
                                )
                        
                        # Convert list to semicolon-separated string
                        new_secondary = "; ".join(new_secondary_list) if new_secondary_list else ""
                        
                        # Auto-save when values change
                        # "Not Set" saves as empty string, "None" is a valid value for bodyweight equipment
                        save_equip = "" if new_equipment == "Not Set" else new_equipment
                        save_primary = "" if new_primary in ["Not Set", "None"] else new_primary
                        # If Primary is None or Not Set, force Secondary to be empty
                        save_secondary = "" if new_primary in ["None", "Not Set"] else new_secondary
                        
                        # Check if anything changed
                        if (save_equip != ex_equipment or 
                            save_primary != ex_muscle or 
                            save_secondary != ex_other_muscles):
                            save_custom_exercise(sel_exercise, save_equip, save_primary, save_secondary)
                            st.success("✅ Changes saved", icon="✅")
                            st.rerun()
                    else:
                        # Standard exercise - show static display
                        equip_display = ex_equipment if ex_equipment and ex_equipment.strip() else "Not Set"
                        
                        # Primary and Secondary Muscle Groups logic:
                        # - If Primary is defined: show Primary, Secondary defaults to "None" if not set
                        # - If Primary is not defined: both show "Not Set"
                        primary_defined = ex_muscle and ex_muscle.strip()
                        if primary_defined:
                            primary_display = ex_muscle
                            secondary_display = ex_other_muscles if ex_other_muscles and ex_other_muscles.strip() else "None"
                        else:
                            primary_display = "Not Set"
                            secondary_display = "Not Set"
                        
                        # Compact display with reduced spacing using single HTML block
                        st.markdown(f"""<div style="line-height: 1.5; margin-bottom: 0.5rem;">
<b>Equipment:</b> {equip_display}<br>
<b>Primary Muscle Group:</b> {primary_display}<br>
<b>Secondary Muscle Group:</b> {secondary_display}
</div>""", unsafe_allow_html=True)

                    st.divider()

                    if ex_data.empty:
                        st.info("暂无该动作的训练记录。")
                    else:
                        # Summary metrics - only Total Sets, Total Volume, Total Workouts
                        total_sets = int(ex_data["metric_set_factor"].sum())
                        total_volume = ex_data["metric_set_volume"].sum()
                        total_workouts = ex_data["workout_id"].nunique()

                        # Metrics row (3 columns) - matching Home page card format
                        mcol1, mcol2, mcol3 = st.columns(3)
                        
                        # Card 1: Total Sets
                        with mcol1:
                            sets_display = f"{total_sets:,} <span style='font-size: 0.7em;'>Sets</span>"
                            card_html = f"""<div>
<div style='font-size: 0.95rem; font-weight: 600; margin-bottom: 5px;'>Total Sets</div>
<h3 style='margin-top: 0px; margin-bottom: 5px;'>{sets_display}</h3>
</div>"""
                            st.markdown(card_html, unsafe_allow_html=True)
                        
                        # Card 2: Total Volume or Total Time
                        with mcol2:
                            if ex_type in ["Duration", "Distance & Duration"]:
                                total_duration = ex_data["duration_seconds"].sum() if "duration_seconds" in ex_data.columns else 0
                                hours = int(total_duration // 3600)
                                mins = int((total_duration % 3600) // 60)
                                if hours > 0:
                                    time_display = f"{hours}h {mins:02d}m"
                                else:
                                    secs = int(total_duration % 60)
                                    time_display = f"{mins}m {secs:02d}s"
                                card_html = f"""<div>
<div style='font-size: 0.95rem; font-weight: 600; margin-bottom: 5px;'>Total Time</div>
<h3 style='margin-top: 0px; margin-bottom: 5px;'>{time_display}</h3>
</div>"""
                            else:
                                converted_vol = convert_weight_for_display(total_volume)
                                vol_str = format_compact_number(converted_vol)
                                unit = get_weight_unit_suffix()
                                vol_display = f"{vol_str} <span style='font-size: 0.7em;'>{unit}</span>"
                                card_html = f"""<div>
<div style='font-size: 0.95rem; font-weight: 600; margin-bottom: 5px;'>Total Volume</div>
<h3 style='margin-top: 0px; margin-bottom: 5px;'>{vol_display}</h3>
</div>"""
                            st.markdown(card_html, unsafe_allow_html=True)
                        
                        # Card 3: Total Workouts
                        with mcol3:
                            workouts_display = f"{total_workouts} <span style='font-size: 0.7em;'>Times</span>"
                            card_html = f"""<div>
<div style='font-size: 0.95rem; font-weight: 600; margin-bottom: 5px;'>Total Workouts</div>
<h3 style='margin-top: 0px; margin-bottom: 5px;'>{workouts_display}</h3>
</div>"""
                            st.markdown(card_html, unsafe_allow_html=True)

                        st.divider()

                        # ==================== Progress Chart (moved before Personal Records) ====================
                        # Define chart options based on exercise type
                        chart_options_map = {
                            "Weight & Reps": ["One Rep Max", "Heaviest Weight", "Best Set Volume", "Session Volume", "Total Reps"],
                            "Weighted Bodyweight": ["One Rep Max", "Heaviest Weight", "Best Set Volume", "Session Volume", "Total Reps"],
                            "Assisted Bodyweight": ["Most Reps (Set)", "Best Set Volume", "Session Reps"],
                            "Bodyweight Reps": ["Most Reps (Set)", "Session Reps"],
                            "Duration": ["Best Time", "Total Time"],
                            "Weight & Distance": ["Heaviest Weight", "Total Volume", "Longest Distance"],
                            "Distance & Duration": ["Best Pace", "Longest Distance", "Total Time"],
                        }
                        
                        chart_options = chart_options_map.get(ex_type, ["Session Volume"])
                        
                        # Title on first row
                        st.markdown("#### 📈 Progress Over Time")
                        
                        # Filter and best value on second row
                        chart_header_col1, chart_header_col2 = st.columns([1, 1])
                        with chart_header_col1:
                            # Chart filter selectbox
                            chart_metric = st.selectbox(
                                "Select metric",
                                options=chart_options,
                                key=f"chart_metric_{sel_exercise}",
                                label_visibility="collapsed",
                            )
                        # col2 will be filled after calculating max value
                        
                        # Aggregate data by date based on selected metric
                        daily_data = ex_data.groupby("date").agg(
                            volume=("metric_set_volume", "sum"),
                            sets=("metric_set_factor", "sum"),
                            max_weight=("weight_kg", "max"),
                            total_reps=("reps", "sum"),
                            max_reps=("reps", "max"),
                            total_duration=("duration_seconds", "sum") if "duration_seconds" in ex_data.columns else ("metric_set_factor", "count"),
                            min_duration=("duration_seconds", "min") if "duration_seconds" in ex_data.columns else ("metric_set_factor", "count"),
                            max_distance=("distance_km", "max") if "distance_km" in ex_data.columns else ("metric_set_factor", "count"),
                        ).reset_index().sort_values("date")
                        daily_data["date"] = pd.to_datetime(daily_data["date"])
                        
                        # Calculate 1RM for each day (best estimated 1RM of the session)
                        # Also return the original weight and reps for hover display
                        def calc_daily_1rm_with_details(group):
                            valid = group[(group["weight_kg"] > 0) & (group["reps"] > 0) & (group["reps"] < 37)]
                            if valid.empty:
                                return pd.Series({"best_1rm": 0, "1rm_weight": 0, "1rm_reps": 0})
                            valid = valid.copy()
                            valid["est_1rm"] = valid["weight_kg"] * (36 / (37 - valid["reps"]))
                            max_idx = valid["est_1rm"].idxmax()
                            best_row = valid.loc[max_idx]
                            return pd.Series({
                                "best_1rm": best_row["est_1rm"],
                                "1rm_weight": best_row["weight_kg"],
                                "1rm_reps": best_row["reps"]
                            })
                        
                        daily_1rm = ex_data.groupby("date").apply(calc_daily_1rm_with_details, include_groups=False).reset_index()
                        daily_1rm["date"] = pd.to_datetime(daily_1rm["date"])
                        daily_data = daily_data.merge(daily_1rm, on="date", how="left")
                        
                        # Calculate best set volume per day (with weight and reps details)
                        def calc_best_set_volume_with_details(group):
                            if "weight_kg" in group.columns and "reps" in group.columns:
                                group = group.copy()
                                group["set_vol"] = group["weight_kg"].fillna(0) * group["reps"].fillna(0)
                                max_idx = group["set_vol"].idxmax()
                                best_row = group.loc[max_idx]
                                return pd.Series({
                                    "best_set_volume": best_row["set_vol"],
                                    "best_set_weight": best_row["weight_kg"],
                                    "best_set_reps": best_row["reps"]
                                })
                            return pd.Series({"best_set_volume": 0, "best_set_weight": 0, "best_set_reps": 0})
                        
                        daily_best_set_vol = ex_data.groupby("date").apply(calc_best_set_volume_with_details, include_groups=False).reset_index()
                        daily_best_set_vol["date"] = pd.to_datetime(daily_best_set_vol["date"])
                        daily_data = daily_data.merge(daily_best_set_vol, on="date", how="left")
                        
                        # Calculate heaviest weight details (weight and reps for that set)
                        def calc_heaviest_weight_details(group):
                            if "weight_kg" in group.columns:
                                valid = group[group["weight_kg"].notna() & (group["weight_kg"] > 0)]
                                if not valid.empty:
                                    max_idx = valid["weight_kg"].idxmax()
                                    best_row = valid.loc[max_idx]
                                    return pd.Series({
                                        "heaviest_weight": best_row["weight_kg"],
                                        "heaviest_reps": best_row.get("reps", 0)
                                    })
                            return pd.Series({"heaviest_weight": 0, "heaviest_reps": 0})
                        
                        daily_heaviest = ex_data.groupby("date").apply(calc_heaviest_weight_details, include_groups=False).reset_index()
                        daily_heaviest["date"] = pd.to_datetime(daily_heaviest["date"])
                        daily_data = daily_data.merge(daily_heaviest, on="date", how="left")
                        
                        # Get all sets for each day (for Session Volume hover)
                        def get_daily_sets(group):
                            if "weight_kg" in group.columns and "reps" in group.columns:
                                valid = group[(group["weight_kg"].notna()) & (group["reps"].notna()) & (group["weight_kg"] > 0) & (group["reps"] > 0)]
                                if not valid.empty:
                                    sets_list = []
                                    for _, row in valid.iterrows():
                                        sets_list.append(f"{row['weight_kg']:.1f}|{int(row['reps'])}")
                                    return ";".join(sets_list)
                            return ""
                        
                        daily_sets = ex_data.groupby("date").apply(get_daily_sets, include_groups=False).reset_index()
                        daily_sets.columns = ["date", "all_sets"]
                        daily_sets["date"] = pd.to_datetime(daily_sets["date"])
                        daily_data = daily_data.merge(daily_sets, on="date", how="left")
                        
                        # Select y-axis data based on metric
                        y_col = "volume"
                        y_label = f"Volume ({get_weight_unit_suffix()})"
                        
                        if chart_metric == "Heaviest Weight":
                            y_col = "max_weight"
                            daily_data["max_weight"] = daily_data["max_weight"].apply(lambda x: convert_weight_for_display(x) if pd.notna(x) else 0)
                            daily_data["heaviest_weight_display"] = daily_data["heaviest_weight"].apply(lambda x: convert_weight_for_display(x) if pd.notna(x) else 0)
                            y_label = f"Weight ({get_weight_unit_suffix()})"
                        elif chart_metric == "One Rep Max":
                            y_col = "best_1rm"
                            daily_data["best_1rm"] = daily_data["best_1rm"].apply(lambda x: convert_weight_for_display(x) if pd.notna(x) else 0)
                            daily_data["1rm_weight_display"] = daily_data["1rm_weight"].apply(lambda x: convert_weight_for_display(x) if pd.notna(x) else 0)
                            y_label = f"Est. 1RM ({get_weight_unit_suffix()})"
                        elif chart_metric == "Best Set Volume":
                            y_col = "best_set_volume"
                            daily_data["best_set_volume"] = daily_data["best_set_volume"].apply(lambda x: convert_weight_for_display(x) if pd.notna(x) else 0)
                            daily_data["best_set_weight_display"] = daily_data["best_set_weight"].apply(lambda x: convert_weight_for_display(x) if pd.notna(x) else 0)
                            y_label = f"Set Volume ({get_weight_unit_suffix()})"
                        elif chart_metric == "Session Volume":
                            y_col = "volume"
                            daily_data["volume"] = daily_data["volume"].apply(lambda x: convert_weight_for_display(x) if pd.notna(x) else 0)
                            y_label = f"Session Volume ({get_weight_unit_suffix()})"
                        elif chart_metric == "Total Reps" or chart_metric == "Session Reps":
                            y_col = "total_reps"
                            y_label = "Reps"
                        elif chart_metric == "Most Reps (Set)":
                            y_col = "max_reps"
                            y_label = "Reps (Best Set)"
                        elif chart_metric == "Best Time":
                            y_col = "min_duration"
                            y_label = "Time (seconds)"
                        elif chart_metric == "Total Time":
                            y_col = "total_duration"
                            y_label = "Time (seconds)"
                        elif chart_metric == "Longest Distance":
                            y_col = "max_distance"
                            y_label = "Distance (km)"
                        elif chart_metric == "Best Pace":
                            # Pace = duration / distance (min/km)
                            if "duration_seconds" in ex_data.columns and "distance_km" in ex_data.columns:
                                pace_data = ex_data[(ex_data["distance_km"] > 0) & (ex_data["duration_seconds"] > 0)].copy()
                                pace_data["pace"] = (pace_data["duration_seconds"] / 60) / pace_data["distance_km"]
                                daily_pace = pace_data.groupby("date")["pace"].min().reset_index()
                                daily_pace["date"] = pd.to_datetime(daily_pace["date"])
                                daily_data = daily_data.merge(daily_pace, on="date", how="left")
                            y_col = "pace"
                            y_label = "Pace (min/km)"
                        
                        if len(daily_data) > 1 and y_col in daily_data.columns:
                            import plotly.express as px
                            import plotly.graph_objects as go
                            
                            # Find max value point (for "Best Pace", lower is better)
                            valid_data = daily_data[daily_data[y_col].notna() & (daily_data[y_col] > 0)]
                            if not valid_data.empty:
                                if chart_metric == "Best Pace":
                                    max_idx = valid_data[y_col].idxmin()  # Lower pace is better
                                else:
                                    max_idx = valid_data[y_col].idxmax()
                                max_row = daily_data.loc[max_idx]
                                max_date = max_row["date"]
                                max_value = max_row[y_col]
                            else:
                                max_date = None
                                max_value = None
                            
                            # Display best value in the right column (chart_header_col2)
                            with chart_header_col2:
                                if max_date is not None and max_value is not None:
                                    # Format date as "Nov 21"
                                    date_str = pd.to_datetime(max_date).strftime("%b %d")
                                    # Format value with appropriate unit
                                    if chart_metric in ["Heaviest Weight", "One Rep Max", "Best Set Volume", "Session Volume", "Total Volume"]:
                                        unit_suffix = get_weight_unit_suffix()
                                        best_display = f"🏆 {max_value:,.0f} {unit_suffix} / {date_str}"
                                    elif chart_metric in ["Total Reps", "Session Reps", "Most Reps (Set)"]:
                                        best_display = f"🏆 {int(max_value):,} Reps / {date_str}"
                                    elif chart_metric in ["Best Time", "Total Time"]:
                                        best_display = f"🏆 {int(max_value):,} sec / {date_str}"
                                    elif chart_metric == "Longest Distance":
                                        best_display = f"🏆 {max_value:.2f} km / {date_str}"
                                    elif chart_metric == "Best Pace":
                                        best_display = f"🏆 {max_value:.2f} min/km / {date_str}"
                                    else:
                                        best_display = f"🏆 {max_value:,.0f} / {date_str}"
                                    st.markdown(f"<p style='text-align: left; margin: 0; padding-top: 8px; font-weight: 500;'>{best_display}</p>", unsafe_allow_html=True)
                            
                            unit_suffix = get_weight_unit_suffix()
                            
                            # Build custom hover template based on chart metric
                            if chart_metric == "One Rep Max":
                                # Create custom hover text for each point
                                daily_data["hover_text"] = daily_data.apply(
                                    lambda row: f"<b>{row['best_1rm']:,.0f} {unit_suffix}</b><br>{row['1rm_weight_display']:,.0f} {unit_suffix} × {int(row['1rm_reps'])} reps<br>{pd.to_datetime(row['date']).strftime('%b %d')}",
                                    axis=1
                                )
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(
                                    x=daily_data["date"],
                                    y=daily_data[y_col],
                                    mode="lines+markers",
                                    line=dict(color="#1f77b4"),
                                    marker=dict(size=8, color="#1f77b4"),
                                    hovertemplate="%{customdata}<extra></extra>",
                                    customdata=daily_data["hover_text"],
                                    showlegend=False,
                                ))
                            elif chart_metric == "Heaviest Weight":
                                # Create custom hover text for each point
                                daily_data["hover_text"] = daily_data.apply(
                                    lambda row: f"<b>{row['heaviest_weight_display']:,.1f} {unit_suffix}</b><br>{row['heaviest_weight_display']:,.1f} {unit_suffix} × {int(row['heaviest_reps'])} reps<br>{pd.to_datetime(row['date']).strftime('%b %d')}",
                                    axis=1
                                )
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(
                                    x=daily_data["date"],
                                    y=daily_data[y_col],
                                    mode="lines+markers",
                                    line=dict(color="#1f77b4"),
                                    marker=dict(size=8, color="#1f77b4"),
                                    hovertemplate="%{customdata}<extra></extra>",
                                    customdata=daily_data["hover_text"],
                                    showlegend=False,
                                ))
                            elif chart_metric == "Best Set Volume":
                                # Create custom hover text for each point
                                daily_data["hover_text"] = daily_data.apply(
                                    lambda row: f"<b>{row['best_set_volume']:,.0f} {unit_suffix}</b><br>{row['best_set_weight_display']:,.1f} {unit_suffix} × {int(row['best_set_reps'])} reps<br>{pd.to_datetime(row['date']).strftime('%b %d')}",
                                    axis=1
                                )
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(
                                    x=daily_data["date"],
                                    y=daily_data[y_col],
                                    mode="lines+markers",
                                    line=dict(color="#1f77b4"),
                                    marker=dict(size=8, color="#1f77b4"),
                                    hovertemplate="%{customdata}<extra></extra>",
                                    customdata=daily_data["hover_text"],
                                    showlegend=False,
                                ))
                            elif chart_metric == "Session Volume":
                                # Create custom hover text with all sets
                                def build_session_volume_hover(row):
                                    date_str = pd.to_datetime(row['date']).strftime('%b %d')
                                    header = f"<b>{row['volume']:,.0f} {unit_suffix}</b>"
                                    sets_str = row.get('all_sets', '')
                                    if sets_str:
                                        sets_lines = []
                                        for s in sets_str.split(';')[:5]:  # Limit to 5 sets to avoid too long hover
                                            parts = s.split('|')
                                            if len(parts) == 2:
                                                w, r = float(parts[0]), int(parts[1])
                                                w_display = convert_weight_for_display(w)
                                                sets_lines.append(f"{w_display:,.1f} {unit_suffix} × {r} reps")
                                        if len(sets_str.split(';')) > 5:
                                            sets_lines.append("...")
                                        sets_text = "<br>".join(sets_lines)
                                        return f"{header}<br>{sets_text}<br>{date_str}"
                                    return f"{header}<br>{date_str}"
                                
                                daily_data["hover_text"] = daily_data.apply(build_session_volume_hover, axis=1)
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(
                                    x=daily_data["date"],
                                    y=daily_data[y_col],
                                    mode="lines+markers",
                                    line=dict(color="#1f77b4"),
                                    marker=dict(size=8, color="#1f77b4"),
                                    hovertemplate="%{customdata}<extra></extra>",
                                    customdata=daily_data["hover_text"],
                                    showlegend=False,
                                ))
                            elif chart_metric in ["Total Reps", "Session Reps"]:
                                # Create custom hover text for each point
                                daily_data["hover_text"] = daily_data.apply(
                                    lambda row: f"<b>{int(row['total_reps']):,} reps</b><br>{pd.to_datetime(row['date']).strftime('%b %d')}",
                                    axis=1
                                )
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(
                                    x=daily_data["date"],
                                    y=daily_data[y_col],
                                    mode="lines+markers",
                                    line=dict(color="#1f77b4"),
                                    marker=dict(size=8, color="#1f77b4"),
                                    hovertemplate="%{customdata}<extra></extra>",
                                    customdata=daily_data["hover_text"],
                                    showlegend=False,
                                ))
                            elif chart_metric == "Most Reps (Set)":
                                # Create custom hover text for each point
                                daily_data["hover_text"] = daily_data.apply(
                                    lambda row: f"<b>{int(row['max_reps']):,} reps</b><br>{pd.to_datetime(row['date']).strftime('%b %d')}",
                                    axis=1
                                )
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(
                                    x=daily_data["date"],
                                    y=daily_data[y_col],
                                    mode="lines+markers",
                                    line=dict(color="#1f77b4"),
                                    marker=dict(size=8, color="#1f77b4"),
                                    hovertemplate="%{customdata}<extra></extra>",
                                    customdata=daily_data["hover_text"],
                                    showlegend=False,
                                ))
                            elif chart_metric == "Best Time":
                                # Format duration as mm:ss
                                def format_duration(seconds):
                                    if pd.isna(seconds) or seconds <= 0:
                                        return "0:00"
                                    mins = int(seconds // 60)
                                    secs = int(seconds % 60)
                                    return f"{mins}:{secs:02d}"
                                
                                daily_data["hover_text"] = daily_data.apply(
                                    lambda row: f"<b>{format_duration(row['min_duration'])}</b><br>{pd.to_datetime(row['date']).strftime('%b %d')}",
                                    axis=1
                                )
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(
                                    x=daily_data["date"],
                                    y=daily_data[y_col],
                                    mode="lines+markers",
                                    line=dict(color="#1f77b4"),
                                    marker=dict(size=8, color="#1f77b4"),
                                    hovertemplate="%{customdata}<extra></extra>",
                                    customdata=daily_data["hover_text"],
                                    showlegend=False,
                                ))
                            elif chart_metric == "Total Time":
                                # Format duration as mm:ss
                                def format_duration(seconds):
                                    if pd.isna(seconds) or seconds <= 0:
                                        return "0:00"
                                    mins = int(seconds // 60)
                                    secs = int(seconds % 60)
                                    return f"{mins}:{secs:02d}"
                                
                                daily_data["hover_text"] = daily_data.apply(
                                    lambda row: f"<b>{format_duration(row['total_duration'])}</b><br>{pd.to_datetime(row['date']).strftime('%b %d')}",
                                    axis=1
                                )
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(
                                    x=daily_data["date"],
                                    y=daily_data[y_col],
                                    mode="lines+markers",
                                    line=dict(color="#1f77b4"),
                                    marker=dict(size=8, color="#1f77b4"),
                                    hovertemplate="%{customdata}<extra></extra>",
                                    customdata=daily_data["hover_text"],
                                    showlegend=False,
                                ))
                            elif chart_metric == "Longest Distance":
                                daily_data["hover_text"] = daily_data.apply(
                                    lambda row: f"<b>{row['max_distance']:.2f} km</b><br>{pd.to_datetime(row['date']).strftime('%b %d')}",
                                    axis=1
                                )
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(
                                    x=daily_data["date"],
                                    y=daily_data[y_col],
                                    mode="lines+markers",
                                    line=dict(color="#1f77b4"),
                                    marker=dict(size=8, color="#1f77b4"),
                                    hovertemplate="%{customdata}<extra></extra>",
                                    customdata=daily_data["hover_text"],
                                    showlegend=False,
                                ))
                            elif chart_metric == "Best Pace":
                                daily_data["hover_text"] = daily_data.apply(
                                    lambda row: f"<b>{row['pace']:.2f} min/km</b><br>{pd.to_datetime(row['date']).strftime('%b %d')}",
                                    axis=1
                                )
                                fig = go.Figure()
                                fig.add_trace(go.Scatter(
                                    x=daily_data["date"],
                                    y=daily_data[y_col],
                                    mode="lines+markers",
                                    line=dict(color="#1f77b4"),
                                    marker=dict(size=8, color="#1f77b4"),
                                    hovertemplate="%{customdata}<extra></extra>",
                                    customdata=daily_data["hover_text"],
                                    showlegend=False,
                                ))
                            else:
                                fig = px.line(
                                    daily_data,
                                    x="date",
                                    y=y_col,
                                    markers=True,
                                    labels={"date": "Date", y_col: y_label},
                                )
                            
                            # Add vertical line at max value date
                            if max_date is not None:
                                fig.add_vline(
                                    x=max_date,
                                    line_width=1,
                                    line_dash="dash",
                                    line_color="#1f77b4",
                                )
                                
                                # Add highlighted marker at max point
                                fig.add_trace(go.Scatter(
                                    x=[max_date],
                                    y=[max_value],
                                    mode="markers",
                                    marker=dict(
                                        size=12,
                                        color="#1f77b4",
                                        line=dict(width=2, color="#1f77b4"),
                                    ),
                                    showlegend=False,
                                    hoverinfo="skip",
                                ))
                            
                            fig.update_layout(
                                height=280,
                                margin=dict(l=20, r=20, t=20, b=20),
                                xaxis_title="",
                                yaxis_title=y_label,
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("需要至少两次训练记录才能显示趋势图。")

                        st.divider()

                        # ==================== Personal Records Section ====================
                        st.markdown("#### 🏆 Personal Records")
                        
                        # Helper function to format date (remove time)
                        def format_record_date(date_val):
                            if pd.isna(date_val):
                                return ""
                            try:
                                return pd.to_datetime(date_val).strftime("%b %d, %Y")
                            except:
                                return str(date_val).split(" ")[0] if " " in str(date_val) else str(date_val)
                        
                        # CSS for fancy record cards
                        st.markdown("""
                        <style>
                        .record-card {
                            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                            border-left: 4px solid #ffc107;
                            border-radius: 8px;
                            padding: 12px 16px;
                            margin-bottom: 10px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                        }
                        .record-title {
                            font-size: 0.85rem;
                            color: #6c757d;
                            margin-bottom: 4px;
                            font-weight: 500;
                        }
                        .record-value {
                            font-size: 1.4rem;
                            font-weight: 700;
                            color: #212529;
                            margin-bottom: 2px;
                        }
                        .record-detail {
                            font-size: 0.9rem;
                            color: #495057;
                        }
                        .record-date {
                            font-size: 0.8rem;
                            color: #868e96;
                            margin-top: 4px;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        if ex_type in ["Weight & Reps", "Weighted Bodyweight"]:
                            unit_suffix = get_weight_unit_suffix()
                            pr_cols = st.columns(2)
                            
                            # Heaviest Weight
                            with pr_cols[0]:
                                if "weight_kg" in ex_data.columns:
                                    weight_data = ex_data[ex_data["weight_kg"].notna() & (ex_data["weight_kg"] > 0)]
                                    if not weight_data.empty:
                                        max_weight_idx = weight_data["weight_kg"].idxmax()
                                        max_weight_row = weight_data.loc[max_weight_idx]
                                        max_weight = convert_weight_for_display(float(max_weight_row["weight_kg"]))
                                        max_weight_reps = int(max_weight_row.get("reps", 0))
                                        max_weight_date = format_record_date(max_weight_row.get("date", ""))
                                        st.markdown(f"""
                                        <div class="record-card">
                                            <div class="record-title">🏋️ Heaviest Weight</div>
                                            <div class="record-value">{max_weight:,.1f} {unit_suffix}</div>
                                            <div class="record-detail">{max_weight:,.1f} {unit_suffix} × {max_weight_reps} reps</div>
                                            <div class="record-date">{max_weight_date}</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                            
                            # Best 1RM
                            with pr_cols[1]:
                                if "weight_kg" in ex_data.columns and "reps" in ex_data.columns:
                                    valid_sets = ex_data[(ex_data["weight_kg"] > 0) & (ex_data["reps"] > 0) & (ex_data["reps"] < 37)]
                                    if not valid_sets.empty:
                                        valid_sets = valid_sets.copy()
                                        valid_sets["est_1rm"] = valid_sets["weight_kg"] * (36 / (37 - valid_sets["reps"]))
                                        max_1rm_idx = valid_sets["est_1rm"].idxmax()
                                        max_1rm_row = valid_sets.loc[max_1rm_idx]
                                        est_1rm = convert_weight_for_display(float(max_1rm_row["est_1rm"]))
                                        est_1rm_weight = convert_weight_for_display(float(max_1rm_row["weight_kg"]))
                                        est_1rm_reps = int(max_1rm_row["reps"])
                                        est_1rm_date = format_record_date(max_1rm_row.get("date", ""))
                                        st.markdown(f"""
                                        <div class="record-card">
                                            <div class="record-title">💪 Best 1RM</div>
                                            <div class="record-value">{est_1rm:,.0f} {unit_suffix}</div>
                                            <div class="record-detail">{est_1rm_weight:,.1f} {unit_suffix} × {est_1rm_reps} reps</div>
                                            <div class="record-date">{est_1rm_date}</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                            
                            pr_cols2 = st.columns(2)
                            
                            # Best Set Volume
                            with pr_cols2[0]:
                                if "weight_kg" in ex_data.columns and "reps" in ex_data.columns:
                                    vol_data = ex_data[(ex_data["weight_kg"] > 0) & (ex_data["reps"] > 0)].copy()
                                    if not vol_data.empty:
                                        vol_data["set_vol"] = vol_data["weight_kg"] * vol_data["reps"]
                                        max_vol_idx = vol_data["set_vol"].idxmax()
                                        max_vol_row = vol_data.loc[max_vol_idx]
                                        best_set_vol = convert_weight_for_display(float(max_vol_row["set_vol"]))
                                        best_vol_weight = convert_weight_for_display(float(max_vol_row["weight_kg"]))
                                        best_vol_reps = int(max_vol_row["reps"])
                                        best_vol_date = format_record_date(max_vol_row.get("date", ""))
                                        st.markdown(f"""
                                        <div class="record-card">
                                            <div class="record-title">📊 Best Set Volume</div>
                                            <div class="record-value">{best_set_vol:,.0f} {unit_suffix}</div>
                                            <div class="record-detail">{best_vol_weight:,.1f} {unit_suffix} × {best_vol_reps} reps</div>
                                            <div class="record-date">{best_vol_date}</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                            
                            # Best Session Volume
                            with pr_cols2[1]:
                                session_volumes = ex_data.groupby("date")["metric_set_volume"].sum()
                                if not session_volumes.empty:
                                    best_session_date = session_volumes.idxmax()
                                    best_session_vol = convert_weight_for_display(float(session_volumes.max()))
                                    best_session_date_fmt = format_record_date(best_session_date)
                                    st.markdown(f"""
                                    <div class="record-card">
                                        <div class="record-title">🔥 Best Session Volume</div>
                                        <div class="record-value">{best_session_vol:,.0f} {unit_suffix}</div>
                                        <div class="record-detail">Total volume in one session</div>
                                        <div class="record-date">{best_session_date_fmt}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        elif ex_type == "Assisted Bodyweight":
                            pr_cols = st.columns(2)
                            
                            with pr_cols[0]:
                                # Best Total Reps (session)
                                session_reps = ex_data.groupby("date")["reps"].sum()
                                if not session_reps.empty:
                                    best_session_date = session_reps.idxmax()
                                    best_session_reps = int(session_reps.max())
                                    best_session_date_fmt = format_record_date(best_session_date)
                                    st.markdown(f"""
                                    <div class="record-card">
                                        <div class="record-title">🔥 Best Total Reps</div>
                                        <div class="record-value">{best_session_reps:,} reps</div>
                                        <div class="record-detail">Total reps in one session</div>
                                        <div class="record-date">{best_session_date_fmt}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            with pr_cols[1]:
                                # Most Reps (Set)
                                if "reps" in ex_data.columns:
                                    reps_data = ex_data[ex_data["reps"].notna() & (ex_data["reps"] > 0)]
                                    if not reps_data.empty:
                                        max_reps_idx = reps_data["reps"].idxmax()
                                        max_reps_row = reps_data.loc[max_reps_idx]
                                        max_reps = int(max_reps_row["reps"])
                                        max_reps_date = format_record_date(max_reps_row.get("date", ""))
                                        st.markdown(f"""
                                        <div class="record-card">
                                            <div class="record-title">💪 Most Reps (Set)</div>
                                            <div class="record-value">{max_reps:,} reps</div>
                                            <div class="record-detail">Best single set</div>
                                            <div class="record-date">{max_reps_date}</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                        
                        elif ex_type == "Bodyweight Reps":
                            pr_cols = st.columns(2)
                            
                            with pr_cols[0]:
                                # Best Set
                                if "reps" in ex_data.columns:
                                    reps_data = ex_data[ex_data["reps"].notna() & (ex_data["reps"] > 0)]
                                    if not reps_data.empty:
                                        max_reps_idx = reps_data["reps"].idxmax()
                                        max_reps_row = reps_data.loc[max_reps_idx]
                                        max_reps = int(max_reps_row["reps"])
                                        max_reps_date = format_record_date(max_reps_row.get("date", ""))
                                        st.markdown(f"""
                                        <div class="record-card">
                                            <div class="record-title">💪 Best Set</div>
                                            <div class="record-value">{max_reps:,} reps</div>
                                            <div class="record-detail">Best single set</div>
                                            <div class="record-date">{max_reps_date}</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                            
                            with pr_cols[1]:
                                # Most Session Reps
                                session_reps = ex_data.groupby("date")["reps"].sum()
                                if not session_reps.empty:
                                    best_session_date = session_reps.idxmax()
                                    best_session_reps = int(session_reps.max())
                                    best_session_date_fmt = format_record_date(best_session_date)
                                    st.markdown(f"""
                                    <div class="record-card">
                                        <div class="record-title">🔥 Most Session Reps</div>
                                        <div class="record-value">{best_session_reps:,} reps</div>
                                        <div class="record-detail">Total reps in one session</div>
                                        <div class="record-date">{best_session_date_fmt}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        elif ex_type == "Duration":
                            if "duration_seconds" in ex_data.columns:
                                dur_data = ex_data[ex_data["duration_seconds"].notna() & (ex_data["duration_seconds"] > 0)]
                                if not dur_data.empty:
                                    pr_cols = st.columns(2)
                                    
                                    with pr_cols[0]:
                                        # Best Time (longest single set)
                                        max_dur_idx = dur_data["duration_seconds"].idxmax()
                                        max_dur_row = dur_data.loc[max_dur_idx]
                                        max_dur = int(max_dur_row["duration_seconds"])
                                        max_dur_date = format_record_date(max_dur_row.get("date", ""))
                                        mins, secs = divmod(max_dur, 60)
                                        st.markdown(f"""
                                        <div class="record-card">
                                            <div class="record-title">⏱️ Best Time</div>
                                            <div class="record-value">{mins}m {secs}s</div>
                                            <div class="record-detail">Longest single set</div>
                                            <div class="record-date">{max_dur_date}</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    with pr_cols[1]:
                                        # Total Time
                                        total_dur = int(dur_data["duration_seconds"].sum())
                                        hours, remainder = divmod(total_dur, 3600)
                                        mins, secs = divmod(remainder, 60)
                                        if hours > 0:
                                            total_time_str = f"{hours}h {mins}m {secs}s"
                                        else:
                                            total_time_str = f"{mins}m {secs}s"
                                        st.markdown(f"""
                                        <div class="record-card">
                                            <div class="record-title">📊 Total Time</div>
                                            <div class="record-value">{total_time_str}</div>
                                            <div class="record-detail">All-time total</div>
                                            <div class="record-date"></div>
                                        </div>
                                        """, unsafe_allow_html=True)
                        
                        elif ex_type == "Weight & Distance":
                            pr_cols = st.columns(2)
                            unit_suffix = get_weight_unit_suffix()
                            
                            with pr_cols[0]:
                                # Heaviest Weight
                                if "weight_kg" in ex_data.columns:
                                    weight_data = ex_data[ex_data["weight_kg"].notna() & (ex_data["weight_kg"] > 0)]
                                    if not weight_data.empty:
                                        max_weight_idx = weight_data["weight_kg"].idxmax()
                                        max_weight_row = weight_data.loc[max_weight_idx]
                                        max_weight = convert_weight_for_display(float(max_weight_row["weight_kg"]))
                                        max_weight_date = format_record_date(max_weight_row.get("date", ""))
                                        st.markdown(f"""
                                        <div class="record-card">
                                            <div class="record-title">🏋️ Heaviest Weight</div>
                                            <div class="record-value">{max_weight:,.1f} {unit_suffix}</div>
                                            <div class="record-detail">Maximum weight carried</div>
                                            <div class="record-date">{max_weight_date}</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                            
                            with pr_cols[1]:
                                # Longest Distance
                                if "distance_km" in ex_data.columns:
                                    dist_data = ex_data[ex_data["distance_km"].notna() & (ex_data["distance_km"] > 0)]
                                    if not dist_data.empty:
                                        max_dist_idx = dist_data["distance_km"].idxmax()
                                        max_dist_row = dist_data.loc[max_dist_idx]
                                        max_dist = float(max_dist_row["distance_km"])
                                        max_dist_date = format_record_date(max_dist_row.get("date", ""))
                                        st.markdown(f"""
                                        <div class="record-card">
                                            <div class="record-title">🛣️ Longest Distance</div>
                                            <div class="record-value">{max_dist:.2f} km</div>
                                            <div class="record-detail">Maximum distance covered</div>
                                            <div class="record-date">{max_dist_date}</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                        
                        elif ex_type == "Distance & Duration":
                            pr_cols = st.columns(2)
                            
                            with pr_cols[0]:
                                # Longest Distance
                                if "distance_km" in ex_data.columns:
                                    dist_data = ex_data[ex_data["distance_km"].notna() & (ex_data["distance_km"] > 0)]
                                    if not dist_data.empty:
                                        max_dist_idx = dist_data["distance_km"].idxmax()
                                        max_dist_row = dist_data.loc[max_dist_idx]
                                        max_dist = float(max_dist_row["distance_km"])
                                        max_dist_date = format_record_date(max_dist_row.get("date", ""))
                                        st.markdown(f"""
                                        <div class="record-card">
                                            <div class="record-title">🛣️ Longest Distance</div>
                                            <div class="record-value">{max_dist:.2f} km</div>
                                            <div class="record-detail">Maximum distance covered</div>
                                            <div class="record-date">{max_dist_date}</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                            
                            with pr_cols[1]:
                                # Longest Time
                                if "duration_seconds" in ex_data.columns:
                                    dur_data = ex_data[ex_data["duration_seconds"].notna() & (ex_data["duration_seconds"] > 0)]
                                    if not dur_data.empty:
                                        max_dur_idx = dur_data["duration_seconds"].idxmax()
                                        max_dur_row = dur_data.loc[max_dur_idx]
                                        max_dur = int(max_dur_row["duration_seconds"])
                                        max_dur_date = format_record_date(max_dur_row.get("date", ""))
                                        mins, secs = divmod(max_dur, 60)
                                        st.markdown(f"""
                                        <div class="record-card">
                                            <div class="record-title">⏱️ Longest Time</div>
                                            <div class="record-value">{mins}m {secs}s</div>
                                            <div class="record-detail">Longest single session</div>
                                            <div class="record-date">{max_dur_date}</div>
                                        </div>
                                        """, unsafe_allow_html=True)

                        # ==================== Set Records (Weight & Reps only) ====================
                        if ex_type in ["Weight & Reps", "Weighted Bodyweight"]:
                            st.divider()
                            st.markdown("#### 🎯 Set Records")
                            
                            unit_suffix = get_weight_unit_suffix()
                            
                            # Find max weight for each rep count from 1-15
                            set_records = []
                            for rep_count in range(1, 16):
                                rep_data = ex_data[(ex_data["reps"] == rep_count) & (ex_data["weight_kg"] > 0)]
                                if not rep_data.empty:
                                    max_idx = rep_data["weight_kg"].idxmax()
                                    max_row = rep_data.loc[max_idx]
                                    max_wt = convert_weight_for_display(float(max_row["weight_kg"]))
                                    rec_date = max_row.get("date", "")
                                    # Format date
                                    try:
                                        date_fmt = pd.to_datetime(rec_date).strftime("%b %d, %Y")
                                    except:
                                        date_fmt = str(rec_date).split(" ")[0] if " " in str(rec_date) else str(rec_date)
                                    set_records.append({
                                        "reps": rep_count,
                                        "weight": f"{max_wt:,.1f} {unit_suffix}",
                                        "date": date_fmt
                                    })
                            
                            if set_records:
                                # Build HTML table with centered text and 2:6:4 column ratio
                                table_html = '<style>.set-records-table{width:100%;border-collapse:collapse;font-size:0.95rem}.set-records-table th{background:#f8f9fa;padding:10px 8px;text-align:center;font-weight:600;border-bottom:2px solid #dee2e6;color:#495057}.set-records-table td{padding:8px;text-align:center;border-bottom:1px solid #e9ecef}.set-records-table tr:hover{background:#f8f9fa}.set-records-table col:nth-child(1){width:16.67%}.set-records-table col:nth-child(2){width:50%}.set-records-table col:nth-child(3){width:33.33%}</style>'
                                table_html += '<table class="set-records-table"><colgroup><col><col><col></colgroup>'
                                table_html += '<thead><tr><th>Reps</th><th>Personal Best</th><th>Date</th></tr></thead><tbody>'
                                for rec in set_records:
                                    table_html += f'<tr><td>{rec["reps"]}</td><td>{rec["weight"]}</td><td>{rec["date"]}</td></tr>'
                                table_html += '</tbody></table>'
                                st.markdown(table_html, unsafe_allow_html=True)
                            else:
                                st.info("暂无 Set Records 数据。")

                        # ==================== Reps Max Calculator (Weight & Reps only) ====================
                        if ex_type in ["Weight & Reps", "Weighted Bodyweight"]:
                            st.divider()
                            st.markdown("#### 🧮 Estimated RM Table")
                            
                            unit_suffix = get_weight_unit_suffix()
                            
                            # Calculate best 1RM first
                            if "weight_kg" in ex_data.columns and "reps" in ex_data.columns:
                                valid_sets = ex_data[(ex_data["weight_kg"] > 0) & (ex_data["reps"] > 0) & (ex_data["reps"] < 37)]
                                if not valid_sets.empty:
                                    valid_sets = valid_sets.copy()
                                    valid_sets["est_1rm"] = valid_sets["weight_kg"] * (36 / (37 - valid_sets["reps"]))
                                    max_1rm_idx = valid_sets["est_1rm"].idxmax()
                                    max_1rm_row = valid_sets.loc[max_1rm_idx]
                                    best_1rm_kg = max_1rm_row["est_1rm"]
                                    best_1rm = convert_weight_for_display(best_1rm_kg)
                                    best_1rm_weight = convert_weight_for_display(float(max_1rm_row["weight_kg"]))
                                    best_1rm_reps = int(max_1rm_row["reps"])
                                    best_1rm_date = max_1rm_row.get("date", "")
                                    # Format date
                                    try:
                                        best_1rm_date_fmt = pd.to_datetime(best_1rm_date).strftime("%b %d, %Y")
                                    except:
                                        best_1rm_date_fmt = str(best_1rm_date).split(" ")[0] if " " in str(best_1rm_date) else str(best_1rm_date)
                                    
                                    # Calculate estimated weight for 1-15 RM using reverse Brzycki formula
                                    # weight = 1RM × (37 - reps) / 36
                                    rm_estimates = []
                                    for rep_count in range(1, 16):
                                        est_weight = best_1rm_kg * (37 - rep_count) / 36
                                        est_weight_display = convert_weight_for_display(est_weight)
                                        rm_estimates.append({
                                            "rm": rep_count,
                                            "est_weight": f"{est_weight_display:,.1f} {unit_suffix}",
                                            "from_set": f"{best_1rm_weight:,.1f} {unit_suffix} × {best_1rm_reps}",
                                            "date": best_1rm_date_fmt
                                        })
                                    
                                    # Build HTML table with centered text and 2:3:3:2 column ratio
                                    table_html = '<style>.rm-table{width:100%;border-collapse:collapse;font-size:0.95rem}.rm-table th{background:#f8f9fa;padding:10px 8px;text-align:center;font-weight:600;border-bottom:2px solid #dee2e6;color:#495057}.rm-table td{padding:8px;text-align:center;border-bottom:1px solid #e9ecef}.rm-table tr:hover{background:#f8f9fa}.rm-table col:nth-child(1){width:20%}.rm-table col:nth-child(2){width:30%}.rm-table col:nth-child(3){width:30%}.rm-table col:nth-child(4){width:20%}</style>'
                                    table_html += '<table class="rm-table"><colgroup><col><col><col><col></colgroup>'
                                    table_html += '<thead><tr><th>RM</th><th>Est. Reps Max</th><th>Est. From</th><th>Date</th></tr></thead><tbody>'
                                    for rm in rm_estimates:
                                        table_html += f'<tr><td>{rm["rm"]}</td><td>{rm["est_weight"]}</td><td>{rm["from_set"]}</td><td>{rm["date"]}</td></tr>'
                                    table_html += '</tbody></table>'
                                    st.markdown(table_html, unsafe_allow_html=True)
                                else:
                                    st.info("暂无足够数据计算 RM 表。")

                with tab2:
                    st.markdown(f"## {sel_exercise} - History")
                    st.divider()

                    # Add CSS to style workout title buttons as links (h2 size)
                    st.markdown("""
                    <style>
                    /* Style workout title buttons as links with h2 size */
                    [class*="st-key-workout_link_"] button {
                        background: transparent !important;
                        border: none !important;
                        color: #1e40af !important;
                        font-weight: 700 !important;
                        font-size: 1.75rem !important;
                        padding: 0 !important;
                        text-align: left !important;
                        cursor: pointer !important;
                        min-height: 0 !important;
                        line-height: 1.3 !important;
                    }
                    [class*="st-key-workout_link_"] button p {
                        font-weight: 700 !important;
                        font-size: 1.75rem !important;
                        margin: 0 !important;
                    }
                    [class*="st-key-workout_link_"] button:hover {
                        text-decoration: underline !important;
                        color: #1e3a8a !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    if ex_data_all.empty:
                        st.info("暂无该动作的训练记录。")
                    else:
                        # Sort workouts by date descending (use ex_data_all to show all sets including warmups)
                        workout_dates = ex_data_all.groupby("workout_id")["start_dt"].first().sort_values(ascending=False)

                        for workout_id in workout_dates.index:
                            wdf = ex_data_all[ex_data_all["workout_id"] == workout_id]
                            workout_title = wdf["title"].iloc[0]
                            workout_date = wdf["start_dt"].iloc[0]
                            workout_date_str = workout_date.strftime("%Y-%m-%d %H:%M") if hasattr(workout_date, "strftime") else str(workout_date)

                            # Workout header - Title as clickable button that navigates to Workouts Review
                            workout_btn_key = f"workout_link_{workout_id}"
                            if st.button(workout_title, key=workout_btn_key, type="tertiary"):
                                st.session_state["selected_workout_id"] = workout_id
                                st.session_state["nav_page"] = "Workouts Review"
                                st.rerun()
                            st.caption(workout_date_str)

                            # Show sets for this exercise in this workout
                            sets_in_workout = wdf.sort_values("set_index") if "set_index" in wdf.columns else wdf

                            # Build numbering for formal sets: exclude warmups and drop-sets from numbering
                            st_types = sets_in_workout["set_type"].fillna("").astype(str).str.lower() if "set_type" in sets_in_workout.columns else pd.Series([""] * len(sets_in_workout))
                            is_warm = st_types.str.contains("warm")
                            is_drop = st_types.str.contains("drop") | st_types.str.contains("dropset") | st_types.str.contains("drop-set")
                            numbered_mask = ~(is_warm | is_drop)
                            numbered_indices = sets_in_workout[numbered_mask].index.tolist()
                            numbered_map = {idx: i + 1 for i, idx in enumerate(numbered_indices)}

                            # Get exercise format for proper display
                            ex_format_local = str(wdf["format"].dropna().astype(str).iloc[0]) if wdf["format"].dropna().any() else ""
                            unit = get_weight_unit_suffix()

                            # Render set header row
                            badge_width_set = 56
                            badge_width_per = 30
                            badge_margin = 16
                            header_padding_left = 20
                            header_html = "<div style='padding:6px 12px; margin-bottom:4px; line-height:1; display:flex; align-items:center;'>"
                            header_html += f"<span style='display:inline-block; vertical-align:middle; width:{badge_width_set}px; padding:4px 6px; border-radius:6px; background:transparent; color:#000; font-weight:700; margin-right:{badge_margin}px; text-align:center; border:none; line-height:1;'>Set</span>"
                            header_html += "</div>"
                            st.markdown(header_html, unsafe_allow_html=True)

                            row_i = 0
                            for idx, s in sets_in_workout.iterrows():
                                st_type = str(s.get("set_type", "")).lower() if s.get("set_type") is not None else ""
                                badge = ""
                                badge_color = "#3b82f6"  # Default blue for normal sets
                                if "warm" in st_type:
                                    badge = "W"
                                    badge_color = "#fbbf24"  # Yellow for warmup
                                elif "drop" in st_type or "dropset" in st_type or "drop-set" in st_type:
                                    badge = "D"
                                    badge_color = "#a855f7"  # Purple for drop sets
                                else:
                                    if idx in numbered_map:
                                        badge = str(numbered_map[idx])
                                    else:
                                        idx_val = s.get("set_index")
                                        if pd.notna(idx_val):
                                            try:
                                                badge = str(int(idx_val))
                                            except Exception:
                                                badge = "1"
                                        else:
                                            badge = "1"

                                # Format record text based on exercise format/type
                                record_text = ""
                                if ex_format_local.upper() == "TIME" or ex_format_local.upper() == "DURATION":
                                    dur = s.get("duration_seconds") if "duration_seconds" in s.index else None
                                    if pd.notna(dur) and dur:
                                        try:
                                            ds = int(dur)
                                            mins = ds // 60
                                            secs = ds % 60
                                            record_text = f"{mins}m {secs}s"
                                        except Exception:
                                            record_text = str(dur)
                                    else:
                                        record_text = "-"
                                elif ex_format_local.upper() in ("DISTANCE & DURATION", "DISTANCE"):
                                    if "distance_km" in s.index and pd.notna(s.get("distance_km")):
                                        record_text = f"{float(s.get('distance_km')):.2f} {get_distance_unit_suffix()}"
                                    elif "distance_miles" in s.index and pd.notna(s.get("distance_miles")):
                                        record_text = f"{float(s.get('distance_miles')):.2f} MI"
                                    else:
                                        record_text = "-"
                                else:
                                    # Default: weight & reps style
                                    weight_val = None
                                    if "weight_kg" in s.index and pd.notna(s.get("weight_kg")):
                                        weight_val = float(s.get("weight_kg"))
                                    elif "adjusted_weight" in s.index and pd.notna(s.get("adjusted_weight")):
                                        weight_val = float(s.get("adjusted_weight"))
                                    elif "weight_lbs" in s.index and pd.notna(s.get("weight_lbs")):
                                        try:
                                            weight_val = float(s.get("weight_lbs")) * 0.45359237
                                        except Exception:
                                            weight_val = None
                                    elif "weight" in s.index and pd.notna(s.get("weight")):
                                        try:
                                            weight_val = float(s.get("weight"))
                                        except Exception:
                                            weight_val = None
                                    if weight_val is None:
                                        weight_val = 0.0
                                    weight_disp = convert_weight_for_display(weight_val)
                                    reps = int(s.get("reps", 0) or 0)
                                    record_text = f"{weight_disp:.1f} {unit} × {reps} reps"

                                # Render set row with badge styling matching Workouts Review
                                badge_html = (
                                    f"<span style='display:inline-block; vertical-align:middle; width:{badge_width_set}px; text-align:center; margin-right:{badge_margin}px;'>"
                                    f"<span style='display:inline-block; vertical-align:middle; width:{badge_width_per}px; padding:4px 6px; border-radius:6px; background:{badge_color}; color:white; font-weight:700; text-align:center; line-height:1;'>{badge}</span>"
                                    f"</span>"
                                )
                                spacer_html = f"<span style='display:inline-block; width:{header_padding_left}px;'></span>"
                                bg = "#ffffff" if (row_i % 2 == 0) else "#f3f4f6"
                                set_row_html = (
                                    f"<div style='background:{bg}; padding:6px 10px; border-radius:6px; margin-bottom:6px; display:flex; align-items:center;'>"
                                    f"{badge_html}{spacer_html}<div style='flex:1; font-size:0.98rem; color:#111;'>{record_text}</div>"
                                    "</div>"
                                )
                                st.markdown(set_row_html, unsafe_allow_html=True)
                                row_i += 1

                            st.markdown("<hr style='margin:16px 0; border:none; border-top:1px solid #e5e7eb;'>", unsafe_allow_html=True)

    # Settings page implementation
    if page == "Settings":
        st.markdown("## ⚙️ Settings")
        st.caption("Customize your Hevy Analyzer experience")
        
        # ==================== Section 1: Display Preferences ====================
        st.markdown("### 📐 Display Preferences")
        
        row1_col1, row1_col2 = st.columns(2)
        
        with row1_col1:
            with st.container(border=True):
                col_label, col_ctrl = st.columns([2, 1])
                with col_label:
                    st.markdown("**⚖️ Weight Unit**")
                    st.caption("How weights and volumes are displayed")
                with col_ctrl:
                    weight_options = {"kg": "Kilograms (kg)", "lbs": "Pounds (lbs)"}
                    current_weight_unit = st.session_state.get("weight_unit_preference", "kg")
                    weight_keys = list(weight_options.keys())
                    weight_index = weight_keys.index(current_weight_unit) if current_weight_unit in weight_keys else 0
                    weight_choice = st.selectbox(
                        "Weight Unit",
                        options=weight_keys,
                        format_func=lambda opt: weight_options[opt],
                        index=weight_index,
                        key="settings_weight_unit",
                        label_visibility="collapsed",
                    )
                    if weight_choice != current_weight_unit:
                        st.session_state["weight_unit_preference"] = weight_choice
                        update_user_preferences(weight_unit=weight_choice)
                        st.toast(f"Weight unit set to {weight_options[weight_choice]}")
        
        with row1_col2:
            with st.container(border=True):
                col_label, col_ctrl = st.columns([2, 1])
                with col_label:
                    st.markdown("**📏 Distance Unit**")
                    st.caption("How distances are displayed")
                with col_ctrl:
                    distance_options = {"kilometers": "Kilometers (km)", "miles": "Miles (mi)"}
                    current_distance_unit = st.session_state.get("distance_unit_preference", "kilometers")
                    distance_keys = list(distance_options.keys())
                    distance_index = distance_keys.index(current_distance_unit) if current_distance_unit in distance_keys else 0
                    distance_choice = st.selectbox(
                        "Distance Unit",
                        options=distance_keys,
                        format_func=lambda opt: distance_options[opt],
                        index=distance_index,
                        key="settings_distance_unit",
                        label_visibility="collapsed",
                    )
                    if distance_choice != current_distance_unit:
                        st.session_state["distance_unit_preference"] = distance_choice
                        update_user_preferences(distance_unit=distance_choice)
                        st.toast(f"Distance unit set to {distance_options[distance_choice]}")
        
        row2_col1, row2_col2 = st.columns(2)
        
        with row2_col1:
            with st.container(border=True):
                col_label, col_ctrl = st.columns([2, 1])
                with col_label:
                    st.markdown("**📅 Week Starts On**")
                    st.caption("Controls how weeks are grouped in charts")
                with col_ctrl:
                    week_start = st.selectbox(
                        "Week Start",
                        ["Monday", "Sunday"],
                        index=0 if st.session_state.week_start == "Monday" else 1,
                        key="settings_week_start",
                        label_visibility="collapsed",
                    )
                    if week_start != st.session_state.week_start:
                        st.session_state.week_start = week_start
                        update_user_preferences(week_start=week_start)
                        st.toast(f"Week start updated to {week_start}")
                        trigger_rerun()
        
        with row2_col2:
            with st.container(border=True):
                col_label, col_ctrl = st.columns([2, 1])
                with col_label:
                    st.markdown("**🏋️ Body Weight**")
                    st.caption("Used for bodyweight exercise calculations")
                with col_ctrl:
                    body_weight_value = st.number_input(
                        "Body Weight (kg)",
                        min_value=30.0,
                        max_value=200.0,
                        value=st.session_state.body_weight_setting,
                        step=0.5,
                        key="settings_body_weight",
                        label_visibility="collapsed",
                    )
                    if body_weight_value != st.session_state.body_weight_setting:
                        st.session_state.body_weight_setting = body_weight_value
                        st.session_state["user_body_weight"] = body_weight_value
                        update_user_preferences(body_weight=body_weight_value)
                        st.toast(f"Body weight updated to {body_weight_value} kg")
        
        st.markdown("")
        
        # ==================== Section 2: Calculation Settings ====================
        st.markdown("### 🧮 Calculation Settings")
        
        # CSS to align toggle to the right
        st.markdown("""
        <style>
        /* Align the toggle container and toggle itself to the right */
        .st-key-settings_include_warmup_sets,
        .st-key-settings_include_bodyweight {
            display: flex;
            justify-content: flex-end;
            width: 100%;
        }
        .st-key-settings_include_warmup_sets .stCheckbox,
        .st-key-settings_include_bodyweight .stCheckbox {
            justify-content: flex-end;
        }
        </style>
        """, unsafe_allow_html=True)
        
        calc_col1, calc_col2 = st.columns(2)
        
        with calc_col1:
            # Include Warmup Sets
            with st.container(border=True):
                col_label, col_ctrl = st.columns([2, 1])
                with col_label:
                    st.markdown("**🔥 Include Warmup Sets**")
                    st.caption("Count warmup sets in volume and set totals")
                with col_ctrl:
                    include_warmups_current = st.session_state.get("include_warmup_sets", False)
                    include_choice = st.toggle(
                        "Include Warmup Sets",
                        value=include_warmups_current,
                        key="settings_include_warmup_sets",
                        label_visibility="collapsed",
                    )
                    if include_choice != include_warmups_current:
                        st.session_state["include_warmup_sets"] = bool(include_choice)
                        update_user_preferences(include_warmup_sets=bool(include_choice))
                        status = "enabled" if include_choice else "disabled"
                        st.toast(f"Warmup sets {status} in calculations")
                        trigger_rerun()
            
            # Secondary Muscle Group Factor
            with st.container(border=True):
                col_label, col_ctrl = st.columns([2, 1])
                with col_label:
                    st.markdown("**🎯 Secondary Muscle Factor**")
                    st.caption("Weight for secondary muscle groups (default: 0.5)")
                with col_ctrl:
                    secondary_factor_current = st.session_state.get("secondary_muscle_factor", 0.5)
                    secondary_factor_choice = st.number_input(
                        "Secondary Muscle Factor",
                        min_value=0.0,
                        max_value=1.0,
                        value=float(secondary_factor_current),
                        step=0.1,
                        format="%.1f",
                        key="settings_secondary_muscle_factor",
                        label_visibility="collapsed",
                    )
                    if secondary_factor_choice != secondary_factor_current:
                        st.session_state["secondary_muscle_factor"] = float(secondary_factor_choice)
                        update_user_preferences(secondary_muscle_factor=float(secondary_factor_choice))
                        st.toast(f"Secondary muscle factor set to {secondary_factor_choice:.1f}")
                        trigger_rerun()
        
        with calc_col2:
            # Drop Sets / Myo Reps Factor
            with st.container(border=True):
                col_label, col_ctrl = st.columns([2, 1])
                with col_label:
                    st.markdown("**📉 Drop/Myo Set Factor**")
                    st.caption("Weight for drop sets and myo reps (default: 0.5)")
                with col_ctrl:
                    drop_factor_current = st.session_state.get("drop_set_factor", 0.5)
                    drop_factor_choice = st.number_input(
                        "Drop Set Factor",
                        min_value=0.0,
                        max_value=1.0,
                        value=float(drop_factor_current),
                        step=0.1,
                        format="%.1f",
                        key="settings_drop_set_factor",
                        label_visibility="collapsed",
                    )
                    if drop_factor_choice != drop_factor_current:
                        st.session_state["drop_set_factor"] = float(drop_factor_choice)
                        update_user_preferences(drop_set_factor=float(drop_factor_choice))
                        st.toast(f"Drop/Myo set factor set to {drop_factor_choice:.1f}")
                        trigger_rerun()
            
            # Include Bodyweight in +KG/-KG exercises
            with st.container(border=True):
                col_label, col_ctrl = st.columns([2, 1])
                with col_label:
                    st.markdown("**⚖️ Include Bodyweight**")
                    st.caption("Add bodyweight to weighted/assisted exercises")
                with col_ctrl:
                    include_bw_current = st.session_state.get("include_bodyweight", True)
                    include_bw_choice = st.toggle(
                        "Include Bodyweight",
                        value=include_bw_current,
                        key="settings_include_bodyweight",
                        label_visibility="collapsed",
                    )
                    if include_bw_choice != include_bw_current:
                        st.session_state["include_bodyweight"] = bool(include_bw_choice)
                        update_user_preferences(include_bodyweight=bool(include_bw_choice))
                        status = "enabled" if include_bw_choice else "disabled"
                        st.toast(f"Bodyweight inclusion {status}")
                        trigger_rerun()
        
        st.markdown("")
        
        # ==================== Section 3: Data Management ====================
        st.markdown("### 💾 Data Management")
        
        # CSS to style the CSV upload button similar to Export button
        st.markdown("""
        <style>
        /* Hide dropzone instructions for settings CSV upload */
        .st-key-settings_csv_upload [data-testid="stFileUploaderDropzoneInstructions"] {
            display: none !important;
        }
        .st-key-settings_csv_upload [data-testid="stFileUploaderDropzone"] {
            background: transparent !important;
            padding: 0 !important;
            height: auto !important;
            min-height: auto !important;
            border: none !important;
            gap: 0 !important;
        }
        .st-key-settings_csv_upload .e16n7gab6 {
            width: 100% !important;
        }
        .st-key-settings_csv_upload [data-testid="stBaseButton-secondary"] {
            width: 100% !important;
            border: 1px solid rgba(49, 51, 63, 0.2) !important;
            background-color: white !important;
            font-size: 0 !important;
            line-height: 1.6 !important;
            padding: 0.25rem 0.75rem !important;
        }
        .st-key-settings_csv_upload [data-testid="stBaseButton-secondary"]::before {
            content: "📁 Upload CSV" !important;
            font-size: 14px !important;
            font-family: "Source Sans Pro", sans-serif !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        dm_col1, dm_col2 = st.columns(2)
        
        with dm_col1:
            with st.container(border=True):
                col_label, col_ctrl = st.columns([2, 1])
                with col_label:
                    st.markdown("**📁 Upload CSV**")
                    st.caption("Import workout data from Hevy CSV export")
                with col_ctrl:
                    settings_csv_file = st.file_uploader(
                        "Upload CSV",
                        type=["csv"],
                        key="settings_csv_upload",
                        label_visibility="collapsed",
                    )
                    if settings_csv_file is not None:
                        process_csv_upload(settings_csv_file, switch_to_source=True)
        
        with dm_col2:
            with st.container(border=True):
                col_label, col_ctrl = st.columns([1, 1])
                with col_label:
                    st.markdown("**🔗 Fetch from Hevy API**")
                    render_remember_api_option("settings_remember_api_key")
                with col_ctrl:
                    col_input, col_btn = st.columns([2, 1])
                    with col_input:
                        settings_api_key = st.text_input(
                            "API Key",
                            type="password",
                            value=st.session_state.get("pending_api_key", ""),
                            key="settings_api_key",
                            label_visibility="collapsed",
                            placeholder="API Key",
                        )
                        if settings_api_key != st.session_state.get("pending_api_key", ""):
                            st.session_state["pending_api_key"] = settings_api_key
                    with col_btn:
                        if st.button("Fetch", key="settings_fetch_api", use_container_width=True):
                            schedule_api_fetch(settings_api_key)
        
        st.markdown("")
        
        # ==================== Section 4: Custom Exercises ====================
        st.markdown("### 🎯 Custom Exercises")
        
        custom_ex_df = load_custom_exercises()
        custom_ex_titles = set(custom_ex_df["exercise_title"].tolist()) if len(custom_ex_df) > 0 else set()
        
        # Load equipment and muscle options
        csv_path = APP_DIR / "exercises.csv"
        try:
            exercises_csv = pd.read_csv(csv_path, keep_default_na=False, na_values=[""])
            csv_exercise_titles = set(exercises_csv["exercise_title"].astype(str).str.strip().unique())
            # Handle NaN values properly - convert to string first
            all_equipment = exercises_csv["equipment"].fillna("").astype(str).unique().tolist()
            equipment_options = ["None"] + sorted([e for e in all_equipment if e and e.strip() and e != "None"])
            if "Other" in all_equipment:
                equipment_options = ["None"] + sorted([e for e in equipment_options if e not in ["None", "Other"]]) + ["Other"]
            all_muscles = exercises_csv["primary_muscle"].fillna("").astype(str).unique().tolist()
            muscle_options = sorted([m for m in all_muscles if m and m.strip()])
        except Exception:
            csv_exercise_titles = set()
            equipment_options = ["None", "Barbell", "Dumbbell", "Machine", "Cable", "Bodyweight", "Other"]
            muscle_options = ["Chest", "Back", "Shoulders", "Biceps", "Triceps", "Quadriceps", "Hamstrings", "Glutes", "Abdominals", "Calves"]
        
        # Find unknown exercises from user's workout data
        unknown_exercises = []
        if raw_hevy_df is not None and not raw_hevy_df.empty:
            user_exercise_titles = set(raw_hevy_df["exercise_title"].astype(str).str.strip().unique())
            # Unknown = in user data but not in exercises.csv AND not already in custom_exercises.csv
            custom_ex_titles_stripped = set(str(t).strip() for t in custom_ex_titles)
            unknown_titles = user_exercise_titles - csv_exercise_titles - custom_ex_titles_stripped
            unknown_exercises = sorted(list(unknown_titles))
        
        # Combine: custom exercises (already configured) + unknown exercises (not configured)
        all_custom_titles = list(custom_ex_titles) + unknown_exercises
        custom_count = len(all_custom_titles)
        
        # Import/Export row - CSS to make file uploader look like a button
        st.markdown("""
        <style>
        /* Hide dropzone instructions (icon, text, limit info), keep only button */
        .st-key-upload_custom_exercises [data-testid="stFileUploaderDropzoneInstructions"] {
            display: none !important;
        }
        /* Style the dropzone to look minimal */
        .st-key-upload_custom_exercises [data-testid="stFileUploaderDropzone"] {
            background: transparent !important;
            padding: 0 !important;
            height: auto !important;
            min-height: auto !important;
            border: none !important;
            gap: 0 !important;
        }
        /* Style the button container */
        .st-key-upload_custom_exercises .e16n7gab6 {
            width: 100% !important;
        }
        /* Style the Browse button to match Export button */
        .st-key-upload_custom_exercises [data-testid="stBaseButton-secondary"] {
            width: 100% !important;
            border: 1px solid rgba(49, 51, 63, 0.2) !important;
            background-color: white !important;
            font-size: 0 !important;
            line-height: 1.6 !important;
            padding: 0.25rem 0.75rem !important;
        }
        /* Replace button text with Import - match exact style of Export button */
        .st-key-upload_custom_exercises [data-testid="stBaseButton-secondary"]::before {
            content: "📥 Import" !important;
            font-size: 1rem !important;
            font-family: "Source Sans Pro", sans-serif !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        configured_count = len(custom_ex_df)
        unconfigured_count = len(unknown_exercises)
        
        with st.container(border=True):
            col_label, col_export, col_import = st.columns([2, 1, 1])
            with col_label:
                if custom_count > 0:
                    if unconfigured_count > 0:
                        st.markdown(f"**📋 {custom_count} custom exercise(s)** <span style='color: #f97316; font-size: 12px;'>({unconfigured_count} not configured)</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**📋 {custom_count} custom exercise(s)**")
                    st.caption("Manage exercises not in the standard database")
                else:
                    st.markdown("**📋 No custom exercises**")
                    st.caption("Add from Exercise Review or import CSV")
            with col_export:
                if configured_count > 0:
                    st.download_button(
                        label="📤 Export",
                        data=get_custom_exercises_csv_bytes(),
                        file_name="custom_exercises.csv",
                        mime="text/csv",
                        key="download_custom_exercises",
                        use_container_width=True,
                    )
                else:
                    template_df = pd.DataFrame(columns=["exercise_title", "equipment", "primary_muscle", "secondary_muscles"])
                    template_bytes = template_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📤 Template",
                        data=template_bytes,
                        file_name="custom_exercises_template.csv",
                        mime="text/csv",
                        key="download_custom_exercises_template",
                        use_container_width=True,
                    )
            with col_import:
                uploaded_custom = st.file_uploader(
                    "Import",
                    type=["csv"],
                    key="upload_custom_exercises",
                    label_visibility="collapsed",
                )
                if uploaded_custom is not None:
                    try:
                        new_custom_df = pd.read_csv(uploaded_custom, keep_default_na=False, na_values=[""])
                        required_cols = ["exercise_title", "equipment", "primary_muscle", "secondary_muscles"]
                        missing_cols = [c for c in required_cols if c not in new_custom_df.columns]
                        if missing_cols:
                            st.error(f"Missing: {', '.join(missing_cols)}")
                        else:
                            new_custom_df = new_custom_df[required_cols].fillna("")
                            new_custom_df.to_csv(CUSTOM_EXERCISES_PATH, index=False)
                            st.toast(f"Imported {len(new_custom_df)} exercise(s)")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        # Edit section (show all custom + unknown exercises)
        if custom_count > 0:
            with st.container(border=True):
                st.markdown("**📝 View & Edit Custom Exercises**")
                
                # Build combined list: configured custom exercises + unknown exercises
                all_exercises_to_show = []
                
                # Add configured custom exercises
                for idx, row in custom_ex_df.iterrows():
                    all_exercises_to_show.append({
                        "exercise_title": row["exercise_title"],
                        "equipment": row["equipment"] if row["equipment"] else "",
                        "primary_muscle": row["primary_muscle"] if row["primary_muscle"] else "",
                        "secondary_muscles": row["secondary_muscles"] if row["secondary_muscles"] else "",
                        "is_configured": True,
                    })
                
                # Add unknown exercises (not yet configured)
                for ex_title in unknown_exercises:
                    all_exercises_to_show.append({
                        "exercise_title": ex_title,
                        "equipment": "",
                        "primary_muscle": "",
                        "secondary_muscles": "",
                        "is_configured": False,
                    })
                
                # Column headers (only once at top)
                col_h0, col_h1, col_h2, col_h3 = st.columns([3, 2, 2, 2])
                with col_h0:
                    st.caption("Exercise")
                with col_h1:
                    st.caption("Equipment")
                with col_h2:
                    st.caption("Primary Muscle")
                with col_h3:
                    st.caption("Secondary Muscles")
                
                updated_rows = []
                
                for idx, ex_data in enumerate(all_exercises_to_show):
                    ex_title = ex_data["exercise_title"]
                    is_configured = ex_data["is_configured"]
                    
                    col0, col1, col2, col3 = st.columns([3, 2, 2, 2])
                    
                    with col0:
                        # Show title with indicator for unconfigured
                        if is_configured:
                            st.markdown(f"**{ex_title}**")
                        else:
                            st.markdown(f"**{ex_title}**<br><span style='color: #f97316; font-size: 12px;'>⚠️ Not configured</span>", unsafe_allow_html=True)
                    
                    with col1:
                        # "None" is a valid equipment value (bodyweight), "" means Not Set
                        current_equip = ex_data["equipment"]
                        if current_equip == "" or pd.isna(current_equip):
                            current_equip = "Not Set"
                        equip_opts_with_notset = ["Not Set"] + equipment_options
                        if current_equip not in equip_opts_with_notset:
                            equip_opts_with_notset.append(current_equip)
                        new_equip = st.selectbox(
                            "Equipment",
                            options=equip_opts_with_notset,
                            index=equip_opts_with_notset.index(current_equip) if current_equip in equip_opts_with_notset else 0,
                            key=f"settings_equip_{idx}",
                            label_visibility="collapsed",
                        )
                    
                    with col2:
                        # "None" means explicitly no primary muscle, "" means Not Set
                        current_muscle = ex_data["primary_muscle"]
                        if current_muscle == "" or pd.isna(current_muscle):
                            current_muscle = "Not Set"
                        muscle_opts_with_notset = ["Not Set", "None"] + muscle_options
                        if current_muscle not in muscle_opts_with_notset:
                            muscle_opts_with_notset.append(current_muscle)
                        new_muscle = st.selectbox(
                            "Primary Muscle",
                            options=muscle_opts_with_notset,
                            index=muscle_opts_with_notset.index(current_muscle) if current_muscle in muscle_opts_with_notset else 0,
                            key=f"settings_muscle_{idx}",
                            label_visibility="collapsed",
                        )
                    
                    with col3:
                        # Check if Primary Muscle is None or Not Set - if so, disable Secondary
                        primary_is_none = (new_muscle in ["None", "Not Set"])
                        current_secondary = ex_data["secondary_muscles"] if ex_data["secondary_muscles"] else ""
                        current_secondary_list = [m.strip() for m in current_secondary.replace(",", ";").split(";") if m.strip()]
                        
                        if primary_is_none:
                            # Show disabled placeholder when Primary is None
                            st.selectbox(
                                "Secondary Muscles",
                                options=["None"],
                                index=0,
                                key=f"settings_secondary_{idx}",
                                disabled=True,
                                label_visibility="collapsed",
                            )
                            new_secondary_list = []
                        else:
                            new_secondary_list = st.multiselect(
                                "Secondary Muscles",
                                options=muscle_options,
                                default=[m for m in current_secondary_list if m in muscle_options],
                                key=f"settings_secondary_{idx}",
                                label_visibility="collapsed",
                                placeholder="Select...",
                            )
                    
                    # "Not Set" saves as empty string, "None" is a valid value to save
                    save_equip = "" if new_equip == "Not Set" else new_equip
                    save_primary = "" if new_muscle == "Not Set" else ("" if new_muscle == "None" else new_muscle)
                    # If Primary is None or Not Set, force Secondary to be empty
                    new_secondary = "" if new_muscle in ["None", "Not Set"] else ("; ".join(new_secondary_list) if new_secondary_list else "")
                    
                    updated_rows.append({
                        "exercise_title": ex_title,
                        "equipment": save_equip,
                        "primary_muscle": new_muscle,
                        "secondary_muscles": new_secondary,
                    })
                    
                    st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
                
                if st.button("💾 Save All Changes", key="save_all_custom_exercises", type="primary"):
                    updated_df = pd.DataFrame(updated_rows)
                    updated_df.to_csv(CUSTOM_EXERCISES_PATH, index=False)
                    st.toast("Changes saved!")
                    st.rerun()
        
        return

    if page not in ("Home", "Workouts Review", "Exercise Review", "Settings"):
        st.info("This section is coming soon. Please stay tuned!")
        return

    body_weight_value = st.session_state.body_weight_setting
    raw_hevy_df = raw_hevy_df.copy()
    raw_hevy_df["body_weight"] = body_weight_value
    raw_hevy_df["body_weight"] = pd.to_numeric(raw_hevy_df["body_weight"], errors="coerce")

    exercises_df = load_exercises()

    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "Week"
    if "week_start" not in st.session_state:
        st.session_state.week_start = "Monday"
    if "summary_metric" not in st.session_state:
        st.session_state.summary_metric = "Workouts"

    df = prepare_workout_df(raw_hevy_df, exercises_df)
    df = add_effective_metrics(df)
    df = add_period_columns(df, st.session_state.week_start)
    df = df.sort_values(["date", "workout_id"])

    if df.empty:
        st.warning("数据为空，请检查 hevy_workouts.csv 内容。")
        return

    period_summary = build_period_summary(df, st.session_state.view_mode, st.session_state.week_start)
    
    # Initialize or validate active_period
    periods = period_summary["period_start"].sort_values(ascending=False).tolist()
    latest_period = periods[0] if periods else None
    # If the floating toolbar selectbox was changed in the previous run,
    # sync it into active_period before validation to avoid overwriting
    # the user's toolbar selection (fixes one-run lag and right-arrow issues).
    try:
        sync_active_period_from_widget(periods)
    except Exception:
        # Defensive: don't break UI if sync fails
        pass
    if "active_period" not in st.session_state:
        st.session_state.active_period = latest_period
    elif st.session_state.active_period not in periods:
        # Only reset if the current active_period is truly invalid (e.g., after switching view modes)
        st.session_state.active_period = latest_period

    # Home page specific content (Workout Summary, Muscle Distribution, etc.)
    if page == "Home":
        st.markdown("---")
        
        # Workout Summary uses its own independent metric selector
        render_workout_summary(period_summary, st.session_state.view_mode, st.session_state.summary_metric)

        st.markdown("---")

        # Muscle Distribution section - will use its own metric selector
        if "distribution_metric" not in st.session_state:
            st.session_state.distribution_metric = "Sets"
        muscle_df = build_muscle_distribution(df, st.session_state.view_mode, st.session_state.distribution_metric, st.session_state.week_start)
        detail_df = build_detailed_muscle_distribution(df, st.session_state.view_mode, st.session_state.distribution_metric, st.session_state.week_start)
        render_muscle_distribution(df, muscle_df, detail_df, st.session_state.distribution_metric, st.session_state.active_period, raw_hevy_df)

        st.markdown("---")

        render_workout_log(df, st.session_state.view_mode, st.session_state.active_period)

        st.markdown("---")

        ex_stats = build_exercise_stats(df, st.session_state.view_mode)

        render_home_floating_controls(periods)


def render_data_source_panel(source_options, source_labels, source_icons, current_source):
    if not st.session_state.get("source_panel_open"):
        return

    panel_placeholder = st.container()
    with panel_placeholder:
        st.markdown(
            "<div class='data-source-panel-wrapper'><div class='data-source-panel'>",
            unsafe_allow_html=True,
        )
        st.markdown("<h4>Data Source</h4>", unsafe_allow_html=True)
        st.caption("Upload a Hevy CSV export or fetch workouts directly from the API.")
        pending_choice = st.session_state.get("pending_source_choice", current_source)
        if pending_choice not in source_options:
            pending_choice = current_source
            st.session_state["pending_source_choice"] = pending_choice
        st.markdown("<div class='data-source-dropdown-label'>Source Type</div>", unsafe_allow_html=True)
        st.markdown("<div class='data-source-dropdown'>", unsafe_allow_html=True)
        selected_source = st.selectbox(
            "Source Type",
            source_options,
            index=source_options.index(pending_choice),
            format_func=lambda x: source_labels.get(x, x),
            key="data_source_selector",
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)
        if selected_source != pending_choice:
            st.session_state["pending_source_choice"] = selected_source
            pending_choice = selected_source

        st.divider()
        csv_uploaded = st.session_state.get("csv_upload_pending", False)

        if pending_choice == "Upload CSV File":
            st.markdown("**Upload CSV Export**")
            uploaded_file = st.file_uploader(
                "Select hevy_workouts.csv",
                type=["csv"],
                key="data_source_csv_uploader",
                help="Export the file from the Hevy mobile app (Settings → Export Workouts).",
            )
            if uploaded_file is not None:
                process_csv_upload(uploaded_file)
                st.session_state["csv_upload_pending"] = True
                csv_uploaded = True
            st.caption("Drop a fresh export anytime to refresh your data cache.")
        else:
            st.markdown("**Hevy API Key**")
            api_key = st.text_input(
                "API Key",
                type="password",
                value=st.session_state.get("pending_api_key", ""),
                key="data_source_api_key",
                help="Hevy API access is available for Hevy Pro users.",
            )
            if api_key != st.session_state.get("pending_api_key", ""):
                st.session_state["pending_api_key"] = api_key
            remember_enabled = render_remember_api_option("data_source_remember_checkbox")
            if remember_enabled:
                saved_key = st.session_state.get("api_key_value", "")
                if saved_key:
                    st.caption(f"Stored key: `{mask_api_key(saved_key)}`")

        st.divider()
        overview_meta = st.session_state["data_source_meta"].get(current_source, {})
        st.markdown("**Current Source Overview**")
        if overview_meta:
            info_col, metric_col = st.columns([1.6, 1])
            with info_col:
                source_label = source_labels.get(current_source, current_source)
                source_icon = source_icons.get(current_source, "📁")
                st.caption(f"{source_icon} Active source: {source_label}")
                if overview_meta.get("updated_at"):
                    st.caption(f"Last synced • {overview_meta['updated_at']}")
                detail_lines = []
                if current_source == "Upload CSV File":
                    file_name = overview_meta.get("file_name") or "hevy_workouts.csv"
                    detail_lines.append(f"File name: `{file_name}`")
                else:
                    remember_enabled = st.session_state.get("remember_api_key", False)
                    saved_key = st.session_state.get("api_key_value", "") if remember_enabled else ""
                    detail_lines.append(
                        "API key storage: **{}**".format(
                            "Saved on this device" if remember_enabled else "Not saved"
                        )
                    )
                    if remember_enabled and saved_key:
                        detail_lines.append(f"Stored key: `{mask_api_key(saved_key)}`")
                    elif remember_enabled:
                        detail_lines.append("Remember is on. The key will store after your next fetch.")

                measurement_info = overview_meta.get("measurement_info") or {}
                if measurement_info:
                    labels = {
                        "weight": "Set weight",
                        "body_weight": "Body weight",
                        "distance": "Distance",
                        "range_of_motion": "Range of motion",
                    }
                    for key_name, label in labels.items():
                        info = measurement_info.get(key_name)
                        raw_col = info.get("raw_column") if info else None
                        if not raw_col:
                            continue
                        raw_unit = (info.get("raw_unit") or "unspecified").upper()
                        normalized_unit = (info.get("normalized_unit") or "").upper()
                        detail_lines.append(
                            f"{label}: `{raw_col}` ({raw_unit}) → stored as {normalized_unit}"
                        )

                for line in detail_lines:
                    st.markdown(f"- {line}")

                for note in overview_meta.get("status_messages", []):
                    st.caption(note)

            with metric_col:
                def _format_metric(value):
                    if value:
                        return f"{value:,}"
                    return "—"

                st.metric("Sets loaded", _format_metric(overview_meta.get("total_sets")))
                st.metric("Workouts", _format_metric(overview_meta.get("workouts_count")))
                if overview_meta.get("success_message"):
                    st.caption(overview_meta["success_message"])
        else:
            st.caption("No data loaded yet. Apply a source to view sync details here.")

        if current_source == "Connect to Hevy API":
            st.markdown("##### API Key Preferences")
            remember_enabled = st.session_state.get("remember_api_key", False)
            saved_key = st.session_state.get("api_key_value", "") if remember_enabled else ""
            info_col, toggle_col = st.columns([1.2, 1])
            with info_col:
                st.markdown("**Stored Key**")
                if remember_enabled and saved_key:
                    st.caption(f"{mask_api_key(saved_key)}")
                elif remember_enabled:
                    st.caption("Remember is on. The key stores after your next fetch.")
                else:
                    st.caption("No key stored on this device.")
            with toggle_col:
                st.markdown("**Remember Key**")
                render_remember_api_option("settings_remember_api_checkbox_inline")

        st.divider()
        st.markdown("<div class='data-source-actions'>", unsafe_allow_html=True)
        col_apply, col_close = st.columns([2, 1], gap="small")
        pending_choice = st.session_state.get("pending_source_choice", current_source)
        pending_api = st.session_state.get("pending_api_key", "")
        remember_flag = st.session_state.get("remember_api_key", False)
        saved_api = st.session_state.get("api_key_value", "") if remember_flag else ""
        source_changed = pending_choice != current_source
        api_changed = (
            pending_choice == "Connect to Hevy API" and pending_api != saved_api
        )
        api_ready = pending_choice == "Connect to Hevy API" and bool((pending_api or "").strip())
        has_changes = source_changed or api_changed or csv_uploaded or api_ready
        apply_disabled = not has_changes
        with col_apply:
            apply_clicked = st.button(
                "Apply Source",
                key="data_source_apply_button",
                disabled=apply_disabled,
                use_container_width=True,
            )
        with col_close:
            close_clicked = st.button(
                "Close",
                key="data_source_close_button",
                use_container_width=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        if apply_clicked:
            new_choice = st.session_state.get("pending_source_choice", current_source)
            new_api = st.session_state.get("pending_api_key", "")
            if new_choice == "Connect to Hevy API":
                clean_api = (new_api or "").strip()
                if not clean_api:
                    st.session_state.setdefault("header_messages", [])
                    st.session_state["header_messages"].append(
                        ("error", "Hevy API key is required to fetch data."),
                    )
                else:
                    st.session_state["data_source_choice"] = new_choice
                    st.session_state["pending_source_choice"] = new_choice
                    st.session_state["csv_upload_pending"] = False
                    st.session_state["source_panel_open"] = False
                    schedule_api_fetch(clean_api)
            else:
                st.session_state["data_source_choice"] = new_choice
                st.session_state["pending_source_choice"] = new_choice
                st.session_state["csv_upload_pending"] = False
                st.session_state["source_panel_open"] = False
                trigger_rerun()

        if close_clicked:
            st.session_state["source_panel_open"] = False
            trigger_rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
