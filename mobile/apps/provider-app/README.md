# Provider Mobile App

## Overview

The Provider Mobile App is a React Native application designed for healthcare providers to manage insurance claims, verify patient eligibility, and handle administrative tasks on-the-go. It enables doctors, nurses, and administrative staff to process claims directly from their mobile devices.

## Features

### Core Features
- 🏥 **Provider Dashboard** - Overview of daily operations
- ✅ **Instant Eligibility** - Real-time patient verification
- 📷 **Claim Submission** - Photo-based claim processing
- 🔐 **Pre-Authorization** - Request approvals instantly
- 👥 **Patient Queue** - Manage patient appointments
- 💳 **Payment Tracking** - Monitor claim payments
- 🔔 **Push Notifications** - Approval alerts
- 🌐 **Offline Support** - Work without internet

### Advanced Features
- 📱 **QR Code Scanner** - Scan patient ID cards
- 🛏️ **Bed Management** - Track bed occupancy
- 💊 **E-Prescribing** - Digital prescriptions
- 📈 **Analytics Dashboard** - Performance metrics
- 👨‍⚕️ **Staff Management** - Manage team access
- 📡 **Facility Switching** - Multi-facility support
- 🆘 **Emergency Mode** - Quick emergency claims
- 🌍 **Multi-language** - Indonesian and English

## Technology Stack

- **Framework**: React Native 0.72+
- **Language**: TypeScript 5.0+
- **State Management**: Redux Toolkit + RTK Query
- **Navigation**: React Navigation 6
- **UI Components**: React Native Paper
- **Styling**: Styled Components
- **API Client**: Axios with retry logic
- **Push Notifications**: Firebase Cloud Messaging
- **Analytics**: Firebase Analytics
- **QR Scanner**: React Native Camera
- **Storage**: AsyncStorage + SQLite
- **Testing**: Jest + Detox

## Platform Support

- **iOS**: 13.0+
- **Android**: API 23+ (Android 6.0+)
- **Tablets**: Optimized for iPad and Android tablets

## Getting Started

### Prerequisites

- Node.js 18+
- React Native CLI
- Xcode 14+ (for iOS)
- Android Studio (for Android)
- CocoaPods (for iOS)
- JDK 11+

### Installation

1. **Navigate to project**
```bash
cd mobile/apps/provider-app
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

# Features
ENABLE_OFFLINE_MODE=true
ENABLE_BED_MANAGEMENT=true
ENABLE_E_PRESCRIBING=true
ENABLE_EMERGENCY_MODE=true

# Security
SESSION_TIMEOUT=900000
ENCRYPTION_KEY=your-encryption-key
CERTIFICATE_PIN=your-cert-pin
```

## Project Structure

```
provider-app/
├── android/              # Android native code
├── ios/                  # iOS native code  
├── src/
│   ├── app/              # App initialization
│   │   ├── App.tsx       # Root component
│   │   ├── store.ts      # Redux store
│   │   └── navigation/   # Navigation setup
│   ├── screens/          # Screen components
│   │   ├── auth/         # Login screens
│   │   ├── dashboard/    # Main dashboard
│   │   ├── eligibility/  # Eligibility check
│   │   ├── claims/       # Claim screens
│   │   ├── patients/     # Patient management
│   │   ├── authorization/ # Pre-auth
│   │   ├── payments/     # Payment tracking
│   │   └── settings/     # App settings
│   ├── components/       # Reusable components
│   │   ├── scanner/      # QR scanner
│   │   ├── forms/        # Form components
│   │   └── charts/       # Chart components
│   ├── services/         # API services
│   │   ├── api/          # API client
│   │   ├── offline/      # Offline sync
│   │   └── notification/ # Push notifications
│   ├── utils/            # Utilities
│   ├── hooks/            # Custom hooks
│   ├── database/         # SQLite schemas
│   ├── assets/           # Images, fonts
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
npm run ios            # Run on iOS
npm run android        # Run on Android
npm run ios:device     # Run on iOS device
npm run android:release # Android release build

# Testing
npm run test           # Unit tests
npm run test:watch     # Watch mode
npm run e2e:ios        # iOS E2E tests
npm run e2e:android    # Android E2E tests

# Code Quality
npm run lint           # ESLint
npm run type-check     # TypeScript
```

## Features Implementation

### QR Code Patient Verification

```typescript
import { RNCamera } from 'react-native-camera';

const PatientScanner = () => {
  const [scanning, setScanning] = useState(true);
  
  const onBarCodeRead = async (event) => {
    if (!scanning) return;
    
    setScanning(false);
    const patientData = JSON.parse(event.data);
    
    // Verify eligibility
    const eligibility = await eligibilityService.verify({
      memberId: patientData.id,
      providerId: currentProvider.id,
      serviceDate: new Date()
    });
    
    navigation.navigate('EligibilityResult', { eligibility });
  };
  
  return (
    <RNCamera
      style={styles.camera}
      onBarCodeRead={onBarCodeRead}
      barCodeTypes={[RNCamera.Constants.BarCodeType.qr]}
    />
  );
};
```

### Offline Claim Management

```typescript
import SQLite from 'react-native-sqlite-storage';

const OfflineClaimService = {
  db: null,
  
  init: async () => {
    this.db = await SQLite.openDatabase({
      name: 'provider_app.db',
      location: 'default'
    });
    
    await this.createTables();
  },
  
  saveClaim: async (claim: Claim) => {
    await this.db.executeSql(
      'INSERT INTO offline_claims (data, created_at) VALUES (?, ?)',
      [JSON.stringify(claim), new Date().toISOString()]
    );
  },
  
  syncClaims: async () => {
    const results = await this.db.executeSql(
      'SELECT * FROM offline_claims WHERE synced = 0'
    );
    
    for (let i = 0; i < results.rows.length; i++) {
      const claim = JSON.parse(results.rows.item(i).data);
      
      try {
        await apiService.submitClaim(claim);
        await this.markSynced(results.rows.item(i).id);
      } catch (error) {
        console.log('Sync failed for claim', results.rows.item(i).id);
      }
    }
  }
};
```

### Real-time Eligibility Check

```typescript
const EligibilityScreen = () => {
  const [memberNumber, setMemberNumber] = useState('');
  const [eligibility, setEligibility] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const checkEligibility = async () => {
    setLoading(true);
    
    try {
      const result = await eligibilityService.verify({
        memberNumber,
        providerId: currentProvider.id,
        serviceDate: new Date(),
        serviceType: 'outpatient'
      });
      
      setEligibility(result);
      
      if (result.eligible) {
        // Show coverage details
        showCoverageModal(result.coverage);
      } else {
        // Show rejection reason
        Alert.alert('Not Eligible', result.reason);
      }
    } catch (error) {
      // Check offline cache
      const cached = await offlineService.getEligibility(memberNumber);
      if (cached) {
        setEligibility(cached);
        Alert.alert('Offline Mode', 'Showing cached eligibility');
      }
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <View>
      <TextInput
        value={memberNumber}
        onChangeText={setMemberNumber}
        placeholder="Enter member number"
      />
      <Button 
        title="Check Eligibility" 
        onPress={checkEligibility}
        loading={loading}
      />
      {eligibility && <EligibilityCard data={eligibility} />}
    </View>
  );
};
```

### Bed Management (Inpatient)

```typescript
interface Bed {
  id: string;
  number: string;
  ward: string;
  status: 'vacant' | 'occupied' | 'reserved' | 'maintenance';
  patient?: Patient;
  class: 'VIP' | 'Class1' | 'Class2' | 'Class3';
}

const BedManagement = () => {
  const [beds, setBeds] = useState<Bed[]>([]);
  const [filter, setFilter] = useState('all');
  
  const filteredBeds = beds.filter(bed => {
    if (filter === 'all') return true;
    return bed.status === filter;
  });
  
  const assignBed = async (bedId: string, patientId: string) => {
    await bedService.assign({
      bedId,
      patientId,
      admissionDate: new Date()
    });
    
    // Update local state
    setBeds(beds.map(bed => 
      bed.id === bedId 
        ? { ...bed, status: 'occupied', patient: { id: patientId } }
        : bed
    ));
  };
  
  return (
    <View>
      <BedStatistics beds={beds} />
      <FilterTabs value={filter} onChange={setFilter} />
      <FlatList
        data={filteredBeds}
        renderItem={({ item }) => (
          <BedCard 
            bed={item}
            onAssign={() => assignBed(item.id)}
            onRelease={() => releaseBed(item.id)}
          />
        )}
      />
    </View>
  );
};
```

### E-Prescribing

```typescript
const EPrescribing = () => {
  const [medications, setMedications] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  
  const searchMedications = async (query: string) => {
    const results = await medicationService.search(query);
    setMedications(results);
  };
  
  const prescribe = async (prescription: Prescription) => {
    // Validate drug interactions
    const interactions = await medicationService.checkInteractions(
      prescription.medications
    );
    
    if (interactions.length > 0) {
      Alert.alert(
        'Drug Interactions Detected',
        interactions.map(i => i.description).join('\n')
      );
    }
    
    // Submit prescription
    await prescriptionService.create({
      ...prescription,
      providerId: currentProvider.id,
      signature: await generateDigitalSignature()
    });
  };
  
  return (
    <View>
      <SearchBar
        value={searchQuery}
        onChangeText={setSearchQuery}
        onSubmit={() => searchMedications(searchQuery)}
      />
      <MedicationList 
        medications={medications}
        onSelect={addToPrescription}
      />
      <PrescriptionForm onSubmit={prescribe} />
    </View>
  );
};
```

### Emergency Mode

```typescript
const EmergencyMode = () => {
  const [patientInfo, setPatientInfo] = useState({});
  
  const submitEmergencyClaim = async () => {
    const claim = {
      type: 'emergency',
      patientInfo,
      providerId: currentProvider.id,
      timestamp: new Date(),
      requiresApproval: false
    };
    
    try {
      // Try online submission
      await claimService.submitEmergency(claim);
    } catch (error) {
      // Save offline for later sync
      await offlineService.saveEmergencyClaim(claim);
      Alert.alert(
        'Saved Offline',
        'Emergency claim will be submitted when connection is restored'
      );
    }
  };
  
  return (
    <ScrollView style={styles.emergency}>
      <Text style={styles.emergencyTitle}>EMERGENCY MODE</Text>
      <TextInput
        placeholder="Patient Name/ID (if available)"
        onChangeText={text => setPatientInfo({ ...patientInfo, name: text })}
      />
      <TextInput
        placeholder="Emergency Description"
        multiline
        onChangeText={text => setPatientInfo({ ...patientInfo, description: text })}
      />
      <Button
        title="SUBMIT EMERGENCY CLAIM"
        onPress={submitEmergencyClaim}
        color="red"
      />
    </ScrollView>
  );
};
```

## State Management

### Redux Store Structure

```typescript
{
  auth: {
    provider: Provider | null,
    facility: Facility | null,
    token: string | null,
    permissions: string[]
  },
  claims: {
    queue: Claim[],
    submitted: Claim[],
    offlineQueue: OfflineClaim[]
  },
  patients: {
    current: Patient | null,
    queue: Patient[],
    eligibilityCache: Map<string, Eligibility>
  },
  facility: {
    beds: Bed[],
    stats: FacilityStats,
    staff: Staff[]
  },
  app: {
    isOnline: boolean,
    syncStatus: 'idle' | 'syncing' | 'error',
    language: 'en' | 'id',
    notifications: Notification[]
  }
}
```

## Testing

### Unit Testing

```typescript
// __tests__/EligibilityCheck.test.tsx
import { renderHook, act } from '@testing-library/react-hooks';
import { useEligibilityCheck } from '../src/hooks/useEligibilityCheck';

describe('useEligibilityCheck', () => {
  it('should cache eligibility results', async () => {
    const { result } = renderHook(() => useEligibilityCheck());
    
    await act(async () => {
      await result.current.checkEligibility('MEMBER123');
    });
    
    expect(result.current.cache.has('MEMBER123')).toBe(true);
  });
  
  it('should handle offline mode', async () => {
    // Simulate offline
    NetInfo.fetch.mockResolvedValue({ isConnected: false });
    
    const { result } = renderHook(() => useEligibilityCheck());
    
    await act(async () => {
      await result.current.checkEligibility('MEMBER123');
    });
    
    expect(result.current.isOffline).toBe(true);
  });
});
```

### E2E Testing

```javascript
// e2e/providerFlow.e2e.js
describe('Provider Claim Flow', () => {
  beforeAll(async () => {
    await device.launchApp();
    await device.loginAsProvider();
  });
  
  it('should submit cashless claim', async () => {
    // Scan patient QR
    await element(by.id('scan-button')).tap();
    await device.mockQRCode('PATIENT_QR_DATA');
    
    // Verify eligibility shown
    await expect(element(by.text('Eligible'))).toBeVisible();
    
    // Add services
    await element(by.id('add-service')).tap();
    await element(by.text('Consultation')).tap();
    
    // Submit claim
    await element(by.id('submit-claim')).tap();
    await expect(element(by.text('Claim Approved'))).toBeVisible();
  });
});
```

## Performance Optimization

### Data Caching Strategy

```typescript
const CacheManager = {
  eligibilityCache: new Map(),
  providerCache: new Map(),
  
  getCachedEligibility: (memberId: string) => {
    const cached = this.eligibilityCache.get(memberId);
    if (cached && Date.now() - cached.timestamp < 3600000) {
      return cached.data;
    }
    return null;
  },
  
  setCachedEligibility: (memberId: string, data: Eligibility) => {
    this.eligibilityCache.set(memberId, {
      data,
      timestamp: Date.now()
    });
  }
};
```

### Optimized List Rendering

```typescript
import { RecyclerListView } from 'recyclerlistview';

const ClaimsList = ({ claims }) => {
  const dataProvider = new DataProvider((r1, r2) => r1.id !== r2.id);
  const layoutProvider = new LayoutProvider(
    index => 0,
    (type, dim) => {
      dim.width = Dimensions.get('window').width;
      dim.height = 120;
    }
  );
  
  return (
    <RecyclerListView
      dataProvider={dataProvider.cloneWithRows(claims)}
      layoutProvider={layoutProvider}
      rowRenderer={(type, data) => <ClaimRow claim={data} />}
    />
  );
};
```

## Security

### Session Management

```typescript
const SessionManager = {
  startSession: async () => {
    const timeout = setTimeout(() => {
      Alert.alert(
        'Session Expired',
        'Please login again for security',
        [{ text: 'OK', onPress: () => logout() }]
      );
    }, SESSION_TIMEOUT);
    
    await AsyncStorage.setItem('sessionTimeout', timeout.toString());
  },
  
  refreshSession: async () => {
    const timeout = await AsyncStorage.getItem('sessionTimeout');
    if (timeout) {
      clearTimeout(parseInt(timeout));
      await this.startSession();
    }
  }
};
```

### Data Protection

```typescript
import * as Keychain from 'react-native-keychain';
import CryptoJS from 'crypto-js';

const SecureDataService = {
  saveCredentials: async (username: string, password: string) => {
    await Keychain.setInternetCredentials(
      'provider-app',
      username,
      password
    );
  },
  
  encryptData: (data: any) => {
    return CryptoJS.AES.encrypt(
      JSON.stringify(data),
      ENCRYPTION_KEY
    ).toString();
  },
  
  decryptData: (encrypted: string) => {
    const decrypted = CryptoJS.AES.decrypt(encrypted, ENCRYPTION_KEY);
    return JSON.parse(decrypted.toString(CryptoJS.enc.Utf8));
  }
};
```

## Build & Release

### iOS Release

```bash
# Clean and build
cd ios
xcodebuild clean
xcodebuild -workspace ProviderApp.xcworkspace \
  -scheme ProviderApp \
  -configuration Release \
  -archivePath ../build/ProviderApp.xcarchive \
  archive
```

### Android Release

```bash
# Generate signed APK
cd android
./gradlew clean
./gradlew assembleRelease

# Generate AAB
./gradlew bundleRelease
```

## App Distribution

### TestFlight (iOS)
```bash
# Upload to TestFlight
xcrun altool --upload-app \
  -f build/ProviderApp.ipa \
  -u developer@claimsaskes.com \
  -p @keychain:AC_PASSWORD
```

### Internal Testing (Android)
```bash
# Upload to Play Console
# Use Google Play Console API or manual upload
```

## Monitoring & Analytics

### Performance Monitoring

```typescript
import perf from '@react-native-firebase/perf';

const trace = await perf().startTrace('claim_submission');
// ... perform claim submission
await trace.stop();
```

### User Analytics

```typescript
import analytics from '@react-native-firebase/analytics';

analytics().logEvent('claim_submitted', {
  provider_id: providerId,
  claim_type: 'cashless',
  amount: claimAmount,
  facility: facilityId
});
```

## Troubleshooting

### Common Issues

1. **Camera not working**
   - Check camera permissions in Info.plist/AndroidManifest
   - Ensure device has camera hardware

2. **Offline sync failing**
   - Check SQLite database integrity
   - Clear offline queue and re-sync

3. **Push notifications not received**
   - Verify FCM configuration
   - Check notification permissions

## Support

- **Documentation**: [Full docs](../../../docs)
- **Provider Support**: provider-support@claims-askes.com
- **Technical Issues**: GitHub Issues
- **Mobile Team**: mobile-dev@claims-askes.com

## License

Proprietary - All rights reserved