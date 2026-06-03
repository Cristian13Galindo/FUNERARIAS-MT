export const environment = {
  production: true,
  apiUrl: `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:5000/api`,
  tenant: {
    slug: 'losolivos',
    name: 'Funeraria Los Olivos',
    logoUrl: 'assets/logos/logoLosOlivos.png',
    primaryColor: '#006338',
    secondaryColor: '#C6A152',
    accentColor: '#D4AF37',
    backgroundColor: '#ffffff',
    textColor: '#333333',
  }
};
