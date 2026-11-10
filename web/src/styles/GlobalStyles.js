import { createGlobalStyle } from 'styled-components';
import { COLORS, TYPOGRAPHY } from './palette';


export const GlobalStyles = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  
  html, body, #root {
    width: 100%;
    min-height: 100vh;
  }

  body {
    font-family: ${TYPOGRAPHY.FONT_FAMILY};
    background-color: ${COLORS.BACKGROUND};
    color: ${COLORS.ON_SURFACE};
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }

  a {
    text-decoration: none;
    color: inherit;
  }

  button {
    cursor: pointer;
    font-family: inherit;
  }

  input, select, textarea {
    font-family: inherit;
  }
`;