export const colors = {
  background: '#0B1220',
  surface: '#151F32',
  surfaceAlt: '#1D2A42',
  border: '#2A3850',
  text: '#F4F6F8',
  textMuted: '#9AA7BD',
  primary: '#3D8BFD',
  success: '#3FBF7F',
  warning: '#E0A83B',
  danger: '#E0563B',

  // Tier colors used on dashboard cards — matches the standards' 4 tiers.
  tierBelow: '#E0563B',
  tierMin: '#E0A83B',
  tierCompetitive: '#3D8BFD',
  tierMax: '#3FBF7F',
};

export const tierColor = (tier?: string) => {
  switch (tier) {
    case 'max':
      return colors.tierMax;
    case 'competitive':
      return colors.tierCompetitive;
    case 'min':
      return colors.tierMin;
    case 'below':
      return colors.tierBelow;
    default:
      return colors.textMuted;
  }
};

export const tierLabel = (tier?: string) => {
  switch (tier) {
    case 'max':
      return 'Max';
    case 'competitive':
      return 'Competitive';
    case 'min':
      return 'Passing';
    case 'below':
      return 'Below standard';
    default:
      return 'No entries yet';
  }
};
