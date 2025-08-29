# Member Mobile App

## Overview

The Member Mobile App is a React Native application that provides health insurance members with convenient mobile access to their insurance benefits, claims submission, provider search, and healthcare services directly from their smartphones.

## Features

### Core Features
- 👤 **Digital ID Card** - Access insurance card anytime
- 📋 **Quick Claims** - Submit claims with photo capture
- 🏥 **Find Providers** - GPS-based provider search
- 💳 **Benefits Overview** - View coverage and limits
- 📆 **Appointments** - Schedule provider visits
- 🔔 **Push Notifications** - Real-time claim updates
- 📷 **Document Scanner** - OCR-powered document capture
- 🌐 **Offline Mode** - Basic features work offline

### Advanced Features
- 📹 **Telemedicine** - Video consultations
- 💊 **Medicine Reminder** - Prescription tracking
- 📊 **Health Tracker** - Integration with health apps
- 👨‍👩‍👧 **Family Members** - Manage dependents
- 🆘 **Emergency Services** - SOS button with location
- 🔒 **Biometric Login** - Face ID/Fingerprint
- 🌍 **Multi-language** - Indonesian and English
- 🌙 **Dark Mode** - Eye-friendly night theme

## Technology Stack

- **Framework**: React Native 0.72+
- **Language**: TypeScript 5.0+
- **State Management**: Redux Toolkit + Redux Persist
- **Navigation**: React Navigation 6
- **UI Components**: React Native Elements + Native Base
- **Styling**: Styled Components
- **API Client**: Axios with interceptors
- **Push Notifications**: Firebase Cloud Messaging
- **Analytics**: Firebase Analytics
- **Crash Reporting**: Crashlytics
- **Camera/Gallery**: React Native Image Picker
- **Maps**: React Native Maps
- **Storage**: AsyncStorage + MMKV
- **Testing**: Jest + Detox

## Platform Support

- **iOS**: 13.0+
- **Android**: API 23+ (Android 6.0+)
- **Tablets**: Responsive design for tablets

## Getting Started

### Prerequisites

- Node.js 18+
- React Native CLI
- Xcode 14+ (for iOS)
- Android Studio (for Android)
- CocoaPods (for iOS)
- JDK 11+

### Installation

1. **Clone and navigate**
```bash
cd mobile/apps/member-app
```

2. **Install dependencies**
```bash
npm install

# iOS only
cd ios && pod install && cd ..
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run the app**

**iOS:**
```bash
npx react-native run-ios
# or
npm run ios
```

**Android:**
```bash
npx react-native run-android
# or
npm run android
```

### Environment Configuration

```bash
# API Configuration
API_BASE_URL=https://api.claims-askes.com
API_TIMEOUT=30000

# Firebase
FIREBASE_API_KEY=your-api-key
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_MESSAGING_SENDER_ID=your-sender-id

# Features
ENABLE_TELEMEDICINE=true
ENABLE_HEALTH_TRACKING=true
ENABLE_BIOMETRIC_AUTH=true

# Maps
GOOGLE_MAPS_API_KEY_IOS=your-ios-key
GOOGLE_MAPS_API_KEY_ANDROID=your-android-key

# Security
ENCRYPTION_KEY=your-encryption-key
PIN_SALT=your-pin-salt
```

## Project Structure

```
member-app/
├── android/              # Android native code
├── ios/                  # iOS native code
├── src/
│   ├── app/              # App initialization
│   │   ├── App.tsx       # Root component
│   │   ├── store.ts      # Redux store
│   │   └── navigation/   # Navigation setup
│   ├── screens/          # Screen components
│   │   ├── auth/         # Login, register, PIN
│   │   ├── home/         # Dashboard
│   │   ├── claims/       # Claims screens
│   │   ├── providers/    # Provider search
│   │   ├── benefits/     # Benefits info
│   │   ├── profile/      # User profile
│   │   └── telemedicine/ # Video consultation
│   ├── components/       # Reusable components
│   │   ├── common/       # Generic components
│   │   ├── cards/        # Card components
│   │   └── modals/       # Modal components
│   ├── services/         # API services
│   ├── utils/            # Utilities
│   ├── hooks/            # Custom hooks
│   ├── assets/           # Images, fonts
│   ├── locales/          # Translations
│   └── types/            # TypeScript types
├── __tests__/            # Unit tests
├── e2e/                  # Detox E2E tests
└── package.json
```

## Development

### Available Scripts

```bash
# Development
npm run start           # Start Metro bundler
npm run ios            # Run on iOS simulator
npm run android        # Run on Android emulator
npm run ios:device     # Run on iOS device
npm run android:device # Run on Android device

# Testing
npm run test           # Run unit tests
npm run test:watch     # Watch mode
npm run test:coverage  # Coverage report
npm run e2e:ios        # iOS E2E tests
npm run e2e:android    # Android E2E tests

# Code Quality
npm run lint           # ESLint
npm run lint:fix       # Fix linting issues
npm run type-check     # TypeScript check

# Build
npm run build:ios      # iOS release build
npm run build:android  # Android release build
```

## Features Implementation

### Digital ID Card

```typescript
import { Card } from 'react-native-elements';
import QRCode from 'react-native-qrcode-svg';

const DigitalIDCard = ({ member }) => {
  return (
    <Card>
      <View style={styles.cardHeader}>
        <Text style={styles.planName}>{member.planName}</Text>
        <Text style={styles.memberNumber}>{member.memberNumber}</Text>
      </View>
      <View style={styles.cardBody}>
        <Text>{member.name}</Text>
        <Text>Valid Until: {member.expiryDate}</Text>
      </View>
      <QRCode
        value={JSON.stringify({
          id: member.id,
          number: member.memberNumber
        })}
        size={100}
      />
    </Card>
  );
};
```

### Camera-based Claim Submission

```typescript
import ImagePicker from 'react-native-image-picker';
import TextRecognition from '@react-native-ml-kit/text-recognition';

const ClaimCamera = () => {
  const captureDocument = async () => {
    const result = await ImagePicker.launchCamera({
      mediaType: 'photo',
      quality: 0.8
    });
    
    if (result.assets?.[0]) {
      // OCR processing
      const ocrResult = await TextRecognition.recognize(result.assets[0].uri);
      
      // Extract relevant data
      const extractedData = extractClaimData(ocrResult.text);
      
      // Submit claim
      await submitClaim({
        image: result.assets[0],
        extractedData
      });
    }
  };
};
```

### GPS-based Provider Search

```typescript
import Geolocation from '@react-native-community/geolocation';
import MapView, { Marker } from 'react-native-maps';

const ProviderMap = () => {
  const [location, setLocation] = useState(null);
  const [providers, setProviders] = useState([]);
  
  useEffect(() => {
    Geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        setLocation({ latitude, longitude });
        
        // Fetch nearby providers
        const nearby = await providerService.getNearby({
          lat: latitude,
          lng: longitude,
          radius: 5000 // 5km
        });
        setProviders(nearby);
      }
    );
  }, []);
  
  return (
    <MapView
      style={styles.map}
      initialRegion={location}
      showsUserLocation
    >
      {providers.map(provider => (
        <Marker
          key={provider.id}
          coordinate={provider.location}
          title={provider.name}
        />
      ))}
    </MapView>
  );
};
```

### Push Notifications

```typescript
import messaging from '@react-native-firebase/messaging';
import PushNotification from 'react-native-push-notification';

const NotificationService = {
  initialize: async () => {
    // Request permission
    const authStatus = await messaging().requestPermission();
    
    if (authStatus === messaging.AuthorizationStatus.AUTHORIZED) {
      // Get FCM token
      const token = await messaging().getToken();
      await apiService.registerDevice(token);
      
      // Handle foreground notifications
      messaging().onMessage(async remoteMessage => {
        PushNotification.localNotification({
          title: remoteMessage.notification.title,
          message: remoteMessage.notification.body,
          data: remoteMessage.data
        });
      });
    }
  }
};
```

### Biometric Authentication

```typescript
import TouchID from 'react-native-touch-id';
import * as Keychain from 'react-native-keychain';

const BiometricAuth = {
  authenticate: async () => {
    try {
      const biometryType = await TouchID.isSupported();
      
      if (biometryType) {
        await TouchID.authenticate('Authenticate to access your account');
        
        // Retrieve stored credentials
        const credentials = await Keychain.getInternetCredentials('claims-app');
        return credentials;
      }
    } catch (error) {
      console.error('Biometric authentication failed', error);
      throw error;
    }
  }
};
```

### Offline Mode

```typescript
import NetInfo from '@react-native-community/netinfo';
import { MMKV } from 'react-native-mmkv';

const storage = new MMKV();

const OfflineManager = {
  syncData: async () => {
    const state = await NetInfo.fetch();
    
    if (state.isConnected) {
      // Sync offline claims
      const offlineClaims = storage.getString('offline_claims');
      if (offlineClaims) {
        const claims = JSON.parse(offlineClaims);
        for (const claim of claims) {
          await apiService.submitClaim(claim);
        }
        storage.delete('offline_claims');
      }
    }
  },
  
  saveOffline: (key: string, data: any) => {
    storage.set(key, JSON.stringify(data));
  }
};
```

## State Management

### Redux Store Structure

```typescript
{
  auth: {
    user: User | null,
    token: string | null,
    biometricEnabled: boolean,
    pinCode: string | null
  },
  claims: {
    list: Claim[],
    drafts: ClaimDraft[],
    offlineQueue: OfflineClaim[]
  },
  providers: {
    nearby: Provider[],
    favorites: Provider[],
    searchHistory: string[]
  },
  health: {
    records: HealthRecord[],
    medications: Medication[],
    appointments: Appointment[]
  },
  app: {
    isOnline: boolean,
    language: 'en' | 'id',
    theme: 'light' | 'dark',
    notifications: boolean
  }
}
```

## Testing

### Unit Testing

```typescript
// __tests__/ClaimSubmission.test.tsx
import { render, fireEvent } from '@testing-library/react-native';
import ClaimSubmission from '../src/screens/claims/ClaimSubmission';

describe('ClaimSubmission', () => {
  it('validates required fields', () => {
    const { getByTestId, getByText } = render(<ClaimSubmission />);
    
    const submitButton = getByTestId('submit-button');
    fireEvent.press(submitButton);
    
    expect(getByText('Provider is required')).toBeTruthy();
    expect(getByText('Service date is required')).toBeTruthy();
  });
});
```

### E2E Testing with Detox

```typescript
// e2e/claimFlow.e2e.js
describe('Claim Flow', () => {
  beforeAll(async () => {
    await device.launchApp();
    await device.loginAsUser();
  });
  
  it('should submit a claim with photo', async () => {
    await element(by.id('tab-claims')).tap();
    await element(by.id('new-claim-button')).tap();
    
    await element(by.id('camera-button')).tap();
    // Simulate camera capture
    await device.takeScreenshot('claim-photo');
    
    await element(by.id('provider-select')).tap();
    await element(by.text('Hospital A')).tap();
    
    await element(by.id('submit-claim')).tap();
    await expect(element(by.text('Claim submitted'))).toBeVisible();
  });
});
```

## Performance Optimization

### Image Optimization

```typescript
import FastImage from 'react-native-fast-image';

const OptimizedImage = ({ source, style }) => (
  <FastImage
    style={style}
    source={{
      uri: source,
      priority: FastImage.priority.normal,
    }}
    resizeMode={FastImage.resizeMode.contain}
  />
);
```

### List Performance

```typescript
import { FlashList } from '@shopify/flash-list';

const ClaimsList = ({ claims }) => (
  <FlashList
    data={claims}
    renderItem={({ item }) => <ClaimCard claim={item} />}
    estimatedItemSize={100}
    keyExtractor={item => item.id}
  />
);
```

## Security

### Data Encryption

```typescript
import CryptoJS from 'crypto-js';

const SecureStorage = {
  save: async (key: string, value: any) => {
    const encrypted = CryptoJS.AES.encrypt(
      JSON.stringify(value),
      ENCRYPTION_KEY
    ).toString();
    
    await AsyncStorage.setItem(key, encrypted);
  },
  
  get: async (key: string) => {
    const encrypted = await AsyncStorage.getItem(key);
    if (encrypted) {
      const decrypted = CryptoJS.AES.decrypt(encrypted, ENCRYPTION_KEY);
      return JSON.parse(decrypted.toString(CryptoJS.enc.Utf8));
    }
    return null;
  }
};
```

### Certificate Pinning

```typescript
// iOS: Info.plist
// Android: network_security_config.xml

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'X-Certificate-Pin': CERTIFICATE_PIN
  }
});
```

## Build & Release

### iOS Release

```bash
# Clean build
cd ios && xcodebuild clean && cd ..

# Archive
xcodebuild -workspace ios/MemberApp.xcworkspace \
  -scheme MemberApp \
  -configuration Release \
  -archivePath build/MemberApp.xcarchive \
  archive

# Export IPA
xcodebuild -exportArchive \
  -archivePath build/MemberApp.xcarchive \
  -exportPath build \
  -exportOptionsPlist ios/ExportOptions.plist
```

### Android Release

```bash
# Generate signed APK
cd android
./gradlew assembleRelease

# Generate AAB for Play Store
./gradlew bundleRelease

# Output: android/app/build/outputs/bundle/release/app-release.aab
```

## App Store Configuration

### iOS App Store
- Bundle ID: com.claimsaskes.member
- Minimum iOS: 13.0
- Requires: Camera, Location, Notifications

### Google Play Store
- Package: com.claimsaskes.member
- Min SDK: 23
- Target SDK: 33
- Permissions: Camera, Location, Storage

## Monitoring

### Crash Reporting

```typescript
import crashlytics from '@react-native-firebase/crashlytics';

// Log custom events
crashlytics().log('Claim submission started');

// Record errors
crashlytics().recordError(error);

// Set user attributes
crashlytics().setUserId(user.id);
crashlytics().setAttribute('plan_type', user.planType);
```

### Analytics

```typescript
import analytics from '@react-native-firebase/analytics';

// Track screens
analytics().logScreenView({
  screen_name: 'Claims',
  screen_class: 'ClaimsScreen'
});

// Track events
analytics().logEvent('claim_submitted', {
  claim_type: 'reimbursement',
  amount: 500000
});
```

## Troubleshooting

### Common Issues

1. **Build Errors iOS**
   ```bash
   cd ios && pod deintegrate && pod install
   ```

2. **Build Errors Android**
   ```bash
   cd android && ./gradlew clean
   ```

3. **Metro Bundler Issues**
   ```bash
   npx react-native start --reset-cache
   ```

## Support

- **Documentation**: [Full docs](../../../docs)
- **Mobile Team**: mobile@claims-askes.com
- **Bug Reports**: GitHub Issues

## License

Proprietary - All rights reserved