PYTHON ?= python3
VENV ?= .venv
SRC := src/github_trend_monitor
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip
VENV_RUN := PYTHONPATH=$(CURDIR)/src $(VENV_PYTHON)

.PHONY: help venv install setup run analyze report pipeline company arxiv calendar

help:
	@echo "Available targets:"
	@echo "  make setup     Create the virtual environment and install dependencies"
	@echo "  make venv      Create the virtual environment in $(VENV)"
	@echo "  make install   Install dependencies into the virtual environment"
	@echo "  make run       Run the GitHub trend scraper"
	@echo "  make analyze   Update stars and analyze repository trends"
	@echo "  make report    Generate the weekly AI report"
	@echo "  make company   Crawl company releases"
	@echo "  make arxiv     Crawl arXiv papers"
	@echo "  make calendar  Generate the calendar JSON"
	@echo "  make pipeline  Run scraper, analysis, and report generation"

$(VENV_PYTHON):
	$(PYTHON) -m venv $(VENV)

venv: $(VENV_PYTHON)

install: venv
	$(VENV_PIP) install -r requirements.txt

setup: install

run: install
	$(VENV_RUN) -m github_trend_monitor.crawlers.scraper_v2

analyze: install
	$(VENV_RUN) -m github_trend_monitor.analysis.analyzer

report: install
	$(VENV_RUN) -m github_trend_monitor.reports.generate_weekly_report

company: install
	$(VENV_RUN) -m github_trend_monitor.crawlers.company_crawler

arxiv: install
	$(VENV_RUN) -m github_trend_monitor.crawlers.fetch_arxiv

calendar: install
	$(VENV_RUN) -m github_trend_monitor.calendar.generate_calendar_json

pipeline: run analyze report
