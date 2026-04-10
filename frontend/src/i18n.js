import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
      "app_title": "Smart Crop Advisor",
      "home_tagline": "Empowering farmers with AI-driven crop predictions",
      "login": "Login",
      "register": "Register",
      "predict": "Predict Crop",
      "dashboard": "Dashboard",
      "logout": "Logout",
      "n_label": "Nitrogen (N)",
      "p_label": "Phosphorus (P)",
      "k_label": "Potassium (K)",
      "ph_label": "Soil pH",
      "city_label": "Your City (for weather)",
      "predict_button": "Get Recommendation",
      "best_crop": "Recommended Crop:",
      "confidence": "Confidence:",
      "fertilizer": "Fertilizer Guide",
      "weather_forecast": "5-Day Weather Forecast",
    }
  },
  hi: {
    translation: {
      "app_title": "स्मार्ट फसल सलाहकार",
      "home_tagline": "एआई-संचालित फसल भविष्यवाणियों के साथ किसानों को सशक्त बनाना",
      "login": "लॉग इन",
      "register": "रजिस्टर करें",
      "predict": "फसल भविष्यवाणी",
      "dashboard": "डैशबोर्ड",
      "logout": "लॉग आउट",
      "n_label": "नाइट्रोजन (N)",
      "p_label": "फास्फोरस (P)",
      "k_label": "पोटेशियम (K)",
      "ph_label": "मिट्टी का पीएच (pH)",
      "city_label": "आपका शहर (मौसम के लिए)",
      "predict_button": "सुझाव प्राप्त करें",
      "best_crop": "अनुशंसित फसल:",
      "confidence": "आत्मविश्वास:",
      "fertilizer": "उर्वरक गाइड",
      "weather_forecast": "5-दिवसीय मौसम का पूर्वानुमान",
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: "en",
    fallbackLng: "en",
    interpolation: { escapeValue: false }
  });

export default i18n;
