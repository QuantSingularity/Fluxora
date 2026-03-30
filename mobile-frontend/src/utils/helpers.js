/**
 * Format a number to a fixed number of decimal places
 * @param {number} num - The number to format
 * @param {number} decimals - Number of decimal places (default: 2)
 * @returns {string} Formatted number string
 */
export const formatNumber = (num, decimals = 2) => {
  if (num === null || num === undefined || Number.isNaN(num)) {
    return "N/A";
  }
  return Number(num).toFixed(decimals);
};

/**
 * Format a date to a readable string
 * @param {Date|string} date - The date to format
 * @param {string} format - Format type ('short', 'long', 'time')
 * @returns {string} Formatted date string
 */
export const formatDate = (date, format = "short") => {
  if (!date) return "N/A";

  const d = typeof date === "string" ? new Date(date) : date;

  if (Number.isNaN(d.getTime())) {
    return "Invalid Date";
  }

  switch (format) {
    case "short":
      return d.toLocaleDateString();
    case "long":
      return d.toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    case "time":
      return d.toLocaleTimeString();
    case "datetime":
      return `${d.toLocaleDateString()} ${d.toLocaleTimeString()}`;
    default:
      return d.toLocaleDateString();
  }
};

/**
 * Calculate percentage change between two numbers
 * @param {number} oldValue - The old value
 * @param {number} newValue - The new value
 * @returns {string} Formatted percentage change with sign
 */
export const calculatePercentageChange = (oldValue, newValue) => {
  if (!oldValue || oldValue === 0) return "N/A";

  const change = ((newValue - oldValue) / oldValue) * 100;
  const sign = change >= 0 ? "+" : "";
  return `${sign}${formatNumber(change, 1)}%`;
};

/**
 * Truncate text to a maximum length with ellipsis
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length (default: 50)
 * @returns {string} Truncated text
 */
export const truncateText = (text, maxLength = 50) => {
  if (!text) return "";
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength - 3)}...`;
};

/**
 * Debounce a function call
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export const debounce = (func, wait = 300) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid email format
 */
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Generate a random ID
 * @returns {string} Random ID string
 */
export const generateId = () => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Deep clone an object
 * @param {Object} obj - Object to clone
 * @returns {Object} Cloned object
 */
export const deepClone = (obj) => {
  return JSON.parse(JSON.stringify(obj));
};

/**
 * Check if object is empty
 * @param {Object} obj - Object to check
 * @returns {boolean} True if object is empty
 */
export const isEmptyObject = (obj) => {
  return Object.keys(obj).length === 0;
};

/**
 * Format file size in bytes to human readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${Math.round((bytes / k ** i) * 100) / 100} ${sizes[i]}`;
};

/**
 * Sleep/delay function
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise} Promise that resolves after delay
 */
export const sleep = (ms) => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

export default {
  formatNumber,
  formatDate,
  calculatePercentageChange,
  truncateText,
  debounce,
  isValidEmail,
  generateId,
  deepClone,
  isEmptyObject,
  formatFileSize,
  sleep,
};
