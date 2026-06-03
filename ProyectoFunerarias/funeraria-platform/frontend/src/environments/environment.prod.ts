export const environment = {
  production: true,
  apiUrl: `http://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:5000/api`,
  tenant: {
    slug: '',
    name: '',
    logoUrl: '',
    primaryColor: '',
    secondaryColor: '',
    accentColor: '',
    backgroundColor: '',
    textColor: '',
  }
};