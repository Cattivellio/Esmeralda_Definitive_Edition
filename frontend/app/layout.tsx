import "@mantine/core/styles.css";
import "@mantine/dates/styles.css";
import "@mantine/notifications/styles.css";
import "@mantine/carousel/styles.css";
import "./globals.css";
import React from "react";
import { Poppins } from "next/font/google";
import {
  MantineProvider,
  ColorSchemeScript,
  mantineHtmlProps,
} from "@mantine/core";
import { Notifications } from "@mantine/notifications";
import { theme } from "../theme";
import GlobalCalculator from "../components/GlobalCalculator";

const poppins = Poppins({
  weight: ['400', '500', '600', '700', '900'],
  subsets: ['latin'],
  variable: '--font-poppins',
});

export const metadata = {
  title: "Escritorio | Esmeralda",
  description: "Sistema Esmeralda Moderno",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "Esmeralda",
  },
  formatDetection: {
    telephone: false,
  },
};

export default function RootLayout({ children }: { children: any }) {
  return (
    <html lang="es" {...mantineHtmlProps} className={poppins.variable}>
      <head>
        <ColorSchemeScript />
        <link rel="shortcut icon" href="/logo.svg" />
        <link rel="apple-touch-icon" href="/logo.svg" />
        <meta
          name="viewport"
          content="minimum-scale=1, initial-scale=1, width=device-width, shrink-to-fit=no, viewport-fit=cover"
        />
        <meta name="theme-color" content="#24cb7c" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
      </head>
      <body style={{ margin: 0, padding: 0 }}>
        <MantineProvider theme={theme} defaultColorScheme="dark" forceColorScheme="dark">
          <Notifications position="bottom-center" />
          <GlobalCalculator />
          {children}
          <script
            dangerouslySetInnerHTML={{
              __html: `
                if ('serviceWorker' in navigator) {
                  window.addEventListener('load', function() {
                    navigator.serviceWorker.register('/sw.js');
                  });
                }
              `,
            }}
          />
        </MantineProvider>
      </body>
    </html>
  );
}
