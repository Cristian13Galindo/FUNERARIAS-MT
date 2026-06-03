export const environment = {
  production: true,
  apiUrl: `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:5000/api`,
  tenant: {
    slug: 'central',
    name: 'Funeraria Central',
    logoUrl: 'assets/logos/logoFuneCentral.jpg',
    primaryColor: '#3b3b3b',
    secondaryColor: '#c8b27f',
    accentColor: '#c8b27f',
    backgroundColor: '#f2f2f2',
    textColor: '#3b3b3b',
  }
};
