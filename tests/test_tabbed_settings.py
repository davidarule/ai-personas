#!/usr/bin/env python3
"""Test script to verify tabbed settings interface"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

def test_tabbed_settings():
    # Setup Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print("Loading dashboard...")
        driver.get("http://localhost:8080")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        
        # Click on Settings
        print("Clicking Settings...")
        settings_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Settings')]")))
        settings_btn.click()
        
        time.sleep(1)
        
        # Check if Azure DevOps tab is active by default
        print("\nChecking Azure DevOps tab...")
        azure_tab = driver.find_element(By.XPATH, "//button[contains(@class, 'tab-button') and contains(text(), 'Azure DevOps')]")
        azure_tab_classes = azure_tab.get_attribute("class")
        print(f"Azure DevOps tab classes: {azure_tab_classes}")
        assert "active" in azure_tab_classes, "Azure DevOps tab should be active by default"
        
        # Check if Azure DevOps content is visible
        azure_content = driver.find_element(By.ID, "azure-devops-tab")
        assert azure_content.is_displayed(), "Azure DevOps content should be visible"
        print("✓ Azure DevOps tab is active and content is visible")
        
        # Check if System content is hidden
        system_content = driver.find_element(By.ID, "system-tab")
        assert not system_content.is_displayed(), "System content should be hidden initially"
        print("✓ System tab content is properly hidden")
        
        # Click on System tab
        print("\nClicking System tab...")
        system_tab = driver.find_element(By.XPATH, "//button[contains(@class, 'tab-button') and contains(text(), 'System')]")
        system_tab.click()
        
        time.sleep(1)
        
        # Check if System tab is now active
        system_tab_classes = system_tab.get_attribute("class")
        print(f"System tab classes: {system_tab_classes}")
        assert "active" in system_tab_classes, "System tab should be active after click"
        
        # Check if System content is now visible
        assert system_content.is_displayed(), "System content should be visible after click"
        print("✓ System tab is active and content is visible")
        
        # Check if Azure DevOps content is now hidden
        assert not azure_content.is_displayed(), "Azure DevOps content should be hidden when System tab is active"
        print("✓ Azure DevOps content is properly hidden")
        
        # Check for log retention fields
        print("\nChecking log retention fields...")
        system_retention = driver.find_element(By.ID, "systemLogRetentionDays")
        persona_retention = driver.find_element(By.ID, "personaLogRetentionDays")
        
        print(f"System log retention value: {system_retention.get_attribute('value')}")
        print(f"Persona log retention value: {persona_retention.get_attribute('value')}")
        
        # Test switching back to Azure DevOps tab
        print("\nSwitching back to Azure DevOps tab...")
        azure_tab.click()
        time.sleep(1)
        
        assert azure_content.is_displayed(), "Azure DevOps content should be visible again"
        assert not system_content.is_displayed(), "System content should be hidden again"
        print("✓ Tab switching works correctly")
        
        print("\n✅ All tests passed! Tabbed settings interface is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        # Take screenshot for debugging
        driver.save_screenshot("test_failure.png")
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    test_tabbed_settings()