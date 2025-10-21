"""
Unit tests for logging utilities.

Tests logging configuration and logger creation.
"""

import pytest
import logging
from unittest.mock import patch, Mock
from src.logging import setup_logging, get_logger


class TestLoggingSetup:
    """Test logging setup functionality."""
    
    def test_setup_logging_default(self):
        """Test logging setup with default parameters."""
        with patch('logging.basicConfig') as mock_basic_config:
            logger = setup_logging()
            
            assert isinstance(logger, logging.Logger)
            assert logger.name == "adversarial-sandbox"
            mock_basic_config.assert_called_once()
    
    def test_setup_logging_custom_level(self):
        """Test logging setup with custom level."""
        with patch('logging.basicConfig') as mock_basic_config:
            logger = setup_logging(level="DEBUG")
            
            # Verify basicConfig was called with DEBUG level
            call_args = mock_basic_config.call_args
            assert call_args[1]["level"] == logging.DEBUG
    
    def test_setup_logging_custom_service_name(self):
        """Test logging setup with custom service name."""
        with patch('logging.basicConfig') as mock_basic_config:
            logger = setup_logging(service_name="test-service")
            
            assert logger.name == "test-service"
    
    def test_setup_logging_custom_format(self):
        """Test logging setup with custom format."""
        custom_format = "%(levelname)s - %(message)s"
        
        with patch('logging.basicConfig') as mock_basic_config:
            logger = setup_logging(log_format=custom_format)
            
            # Verify basicConfig was called with custom format
            call_args = mock_basic_config.call_args
            assert call_args[1]["format"] == custom_format
    
    def test_setup_logging_handler_configuration(self):
        """Test logging setup handler configuration."""
        with patch('logging.basicConfig') as mock_basic_config:
            with patch('logging.StreamHandler') as mock_stream_handler:
                mock_handler = Mock()
                mock_stream_handler.return_value = mock_handler
                
                logger = setup_logging()
                
                # Verify StreamHandler was created
                mock_stream_handler.assert_called_once_with(logging.StreamHandler.return_value)
                
                # Verify basicConfig was called with handler
                call_args = mock_basic_config.call_args
                assert "handlers" in call_args[1]
    
    def test_setup_logging_invalid_level(self):
        """Test logging setup with invalid level."""
        with patch('logging.basicConfig') as mock_basic_config:
            # Should not raise exception, should use default
            logger = setup_logging(level="INVALID")
            
            assert isinstance(logger, logging.Logger)


class TestGetLogger:
    """Test get_logger functionality."""
    
    def test_get_logger_basic(self):
        """Test basic logger creation."""
        logger = get_logger("test.module")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"
    
    def test_get_logger_different_names(self):
        """Test logger creation with different names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        assert logger1.name == "module1"
        assert logger2.name == "module2"
        assert logger1 is not logger2
    
    def test_get_logger_same_name(self):
        """Test that same name returns same logger."""
        logger1 = get_logger("same.module")
        logger2 = get_logger("same.module")
        
        assert logger1 is logger2
    
    def test_get_logger_nested_modules(self):
        """Test logger creation with nested module names."""
        logger = get_logger("platform.services.api_gateway.main")
        
        assert logger.name == "platform.services.api_gateway.main"
    
    def test_get_logger_empty_name(self):
        """Test logger creation with empty name."""
        logger = get_logger("")
        
        assert logger.name == ""


class TestLoggingIntegration:
    """Test logging integration scenarios."""
    
    def test_logging_with_setup_and_get(self):
        """Test using setup_logging and get_logger together."""
        with patch('logging.basicConfig'):
            # Setup logging
            setup_logging(service_name="test-service")
            
            # Get logger for specific module
            logger = get_logger("test.module")
            
            assert logger.name == "test.module"
    
    def test_multiple_loggers_same_service(self):
        """Test multiple loggers for same service."""
        with patch('logging.basicConfig'):
            setup_logging(service_name="test-service")
            
            logger1 = get_logger("module1")
            logger2 = get_logger("module2")
            
            assert logger1.name == "module1"
            assert logger2.name == "module2"
    
    def test_logging_format_consistency(self):
        """Test that logging format is consistent."""
        with patch('logging.basicConfig') as mock_basic_config:
            setup_logging(service_name="test-service")
            
            # Verify format includes service name
            call_args = mock_basic_config.call_args
            format_string = call_args[1]["format"]
            assert "[test-service]" in format_string

