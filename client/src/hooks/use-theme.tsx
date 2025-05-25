import { useEffect, useState } from "react";

type Theme = "dark" | "light" | "system";

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    // Get stored theme from localStorage or use 'system' as default
    return (localStorage.getItem("theme") as Theme) || "light";
  });
  
  // Update theme when it changes
  useEffect(() => {
    const root = window.document.documentElement;
    
    // Remove old theme classes
    root.classList.remove("dark", "light");
    
    // Add new theme class
    if (theme === "system") {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      root.classList.add(systemTheme);
    } else {
      root.classList.add(theme);
    }
    
    // Store theme in localStorage
    localStorage.setItem("theme", theme);
  }, [theme]);
  
  // Watch for system theme changes
  useEffect(() => {
    if (theme === "system") {
      const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
      
      const handleChange = () => {
        const root = window.document.documentElement;
        root.classList.remove("dark", "light");
        root.classList.add(mediaQuery.matches ? "dark" : "light");
      };
      
      mediaQuery.addEventListener("change", handleChange);
      return () => mediaQuery.removeEventListener("change", handleChange);
    }
  }, [theme]);

  return { theme, setTheme };
}
