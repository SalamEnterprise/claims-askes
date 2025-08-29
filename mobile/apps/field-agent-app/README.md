# Field Agent Mobile App

## Overview

The Field Agent Mobile App is a React Native application designed for insurance field agents and sales representatives. It enables them to enroll new members, collect premiums, process simple claims, and provide on-site customer service directly from the field.

## Features

### Core Features
- 👥 **Member Enrollment** - Register new members on-site
- 💳 **Premium Collection** - Process premium payments
- 📋 **Policy Management** - View and update policies
- 📷 **Document Capture** - Scan and upload documents
- 📁 **Claim Assistance** - Help members submit claims
- 📍 **GPS Tracking** - Track agent visits and routes
- 🔔 **Task Management** - Daily tasks and reminders
- 🌐 **Offline Mode** - Work without internet

### Advanced Features
- 📨 **Lead Management** - Track potential customers
- 📊 **Sales Dashboard** - Performance metrics
- 📧 **Quote Generation** - Instant premium quotes
- 🔍 **KYC Verification** - Identity verification
- 💸 **Commission Tracking** - Agent commissions
- 🗺️ **Territory Management** - Assigned territories
- 📅 **Meeting Scheduler** - Customer appointments
- 🌍 **Multi-language** - Indonesian and English

## Technology Stack

- **Framework**: React Native 0.72+
- **Language**: TypeScript 5.0+
- **State Management**: MobX + MobX State Tree
- **Navigation**: React Navigation 6
- **UI Components**: NativeBase + Custom Components
- **Styling**: Styled Components
- **API Client**: Axios with queue management
- **Maps**: React Native Maps + Geolocation
- **Storage**: Realm Database
- **Push Notifications**: OneSignal
- **Analytics**: Mixpanel
- **Testing**: Jest + Detox

## Platform Support

- **iOS**: 13.0+
- **Android**: API 23+ (Android 6.0+)
- **Device Types**: Phones only (optimized for field use)

## Getting Started

### Prerequisites

- Node.js 18+
- React Native CLI
- Xcode 14+ (for iOS)
- Android Studio (for Android)
- CocoaPods (for iOS)

### Installation

1. **Navigate to project**
```bash
cd mobile/apps/field-agent-app
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

4. **Initialize Realm database**
```bash
npm run init:realm
```

5. **Run the app**

**iOS:**
```bash
npx react-native run-ios
```

**Android:**
```bash
npx react-native run-android
```

### Environment Configuration

```bash
# API Configuration
API_BASE_URL=https://api.claims-askes.com
API_TIMEOUT=30000
OFFLINE_SYNC_INTERVAL=300000

# OneSignal
ONESIGNAL_APP_ID=your-app-id

# Mixpanel
MIXPANEL_TOKEN=your-token

# Maps
GOOGLE_MAPS_API_KEY=your-api-key

# Features
ENABLE_OFFLINE_ENROLLMENT=true
ENABLE_GPS_TRACKING=true
ENABLE_COMMISSION_TRACKING=true
ENABLE_KYC_VERIFICATION=true

# Security
ENCRYPTION_KEY=your-encryption-key
SESSION_TIMEOUT=1800000
```

## Project Structure

```
field-agent-app/
├── android/              # Android native code
├── ios/                  # iOS native code
├── src/
│   ├── app/              # App initialization
│   │   ├── App.tsx       # Root component
│   │   ├── stores/       # MobX stores
│   │   └── navigation/   # Navigation setup
│   ├── screens/          # Screen components
│   │   ├── auth/         # Login screens
│   │   ├── dashboard/    # Agent dashboard
│   │   ├── enrollment/   # Member enrollment
│   │   ├── collection/   # Premium collection
│   │   ├── leads/        # Lead management
│   │   ├── policies/     # Policy management
│   │   ├── claims/       # Claim assistance
│   │   ├── tasks/        # Task management
│   │   └── reports/      # Sales reports
│   ├── components/       # Reusable components
│   │   ├── forms/        # Form components
│   │   ├── scanner/      # Document scanner
│   │   └── maps/         # Map components
│   ├── services/         # Services
│   │   ├── api/          # API client
│   │   ├── realm/        # Realm database
│   │   ├── location/     # GPS tracking
│   │   └── sync/         # Offline sync
│   ├── models/           # Data models
│   ├── utils/            # Utilities
│   ├── hooks/            # Custom hooks
│   └── assets/           # Images, fonts
├── __tests__/            # Unit tests
├── e2e/                  # E2E tests
└── package.json
```

## Development

### Available Scripts

```bash
# Development
npm run start           # Start Metro
npm run ios            # iOS simulator
npm run android        # Android emulator
npm run clean          # Clean build

# Database
npm run realm:reset    # Reset Realm database
npm run realm:migrate  # Run migrations

# Testing
npm run test           # Unit tests
npm run e2e:ios        # iOS E2E
npm run e2e:android    # Android E2E

# Code Quality
npm run lint           # ESLint
npm run type-check     # TypeScript
```

## Features Implementation

### Member Enrollment

```typescript
import Realm from 'realm';
import { DocumentScanner } from 'react-native-document-scanner';

const EnrollmentScreen = () => {
  const [memberData, setMemberData] = useState<NewMember>({
    personalInfo: {},
    documents: [],
    plan: null
  });
  
  const scanDocument = async (docType: DocumentType) => {
    const scannedDoc = await DocumentScanner.scanDocument({
      croppedImageQuality: 90,
      responseType: 'base64'
    });
    
    // OCR for KTP (Indonesian ID)
    if (docType === 'KTP') {
      const ocrData = await performOCR(scannedDoc);
      setMemberData({
        ...memberData,
        personalInfo: extractKTPData(ocrData)
      });
    }
    
    // Save document
    const document = {
      type: docType,
      data: scannedDoc,
      timestamp: new Date()
    };
    
    setMemberData({
      ...memberData,
      documents: [...memberData.documents, document]
    });
  };
  
  const submitEnrollment = async () => {
    try {
      // Online submission
      const response = await enrollmentService.submit(memberData);
      Alert.alert('Success', `Member enrolled: ${response.memberNumber}`);
    } catch (error) {
      // Save offline
      await realmService.saveOfflineEnrollment(memberData);
      Alert.alert(
        'Saved Offline',
        'Enrollment will be submitted when online'
      );
    }
  };
  
  return (
    <ScrollView>
      <PersonalInfoForm 
        data={memberData.personalInfo}
        onChange={updatePersonalInfo}
      />
      <DocumentCapture onScan={scanDocument} />
      <PlanSelection onSelect={selectPlan} />
      <Button title="Submit Enrollment" onPress={submitEnrollment} />
    </ScrollView>
  );
};
```

### Premium Collection

```typescript
const PremiumCollection = () => {
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>('cash');
  const [receipt, setReceipt] = useState(null);
  
  const collectPremium = async (member: Member, amount: number) => {
    const payment = {
      memberId: member.id,
      amount,
      method: paymentMethod,
      collectedBy: currentAgent.id,
      location: await getCurrentLocation(),
      timestamp: new Date()
    };
    
    try {
      const response = await paymentService.collectPremium(payment);
      
      // Generate receipt
      const receiptData = await generateReceipt(response);
      setReceipt(receiptData);
      
      // Send receipt via SMS/Email
      await sendReceipt(member.contact, receiptData);
    } catch (error) {
      // Queue for later processing
      await realmService.queuePayment(payment);
    }
  };
  
  const generateReceipt = async (payment: Payment) => {
    return {
      receiptNumber: generateReceiptNumber(),
      ...payment,
      agentName: currentAgent.name,
      signature: await captureSignature()
    };
  };
  
  return (
    <View>
      <MemberSearch onSelect={setSelectedMember} />
      <PaymentMethodSelector 
        value={paymentMethod}
        onChange={setPaymentMethod}
      />
      <AmountInput onConfirm={collectPremium} />
      {receipt && <ReceiptViewer receipt={receipt} />}
    </View>
  );
};
```

### GPS Tracking & Route Management

```typescript
import BackgroundGeolocation from 'react-native-background-geolocation';

const LocationTracker = {
  initialize: async () => {
    await BackgroundGeolocation.configure({
      desiredAccuracy: BackgroundGeolocation.DESIRED_ACCURACY_HIGH,
      distanceFilter: 50,
      stopOnTerminate: false,
      startOnBoot: true,
      interval: 60000,
      fastestInterval: 30000
    });
    
    BackgroundGeolocation.on('location', async (location) => {
      await this.saveLocation(location);
    });
    
    await BackgroundGeolocation.start();
  },
  
  saveLocation: async (location: Location) => {
    const trackingData = {
      agentId: currentAgent.id,
      latitude: location.coords.latitude,
      longitude: location.coords.longitude,
      accuracy: location.coords.accuracy,
      timestamp: location.timestamp,
      activity: location.activity?.type
    };
    
    // Save to Realm
    await realmService.saveTracking(trackingData);
    
    // Sync if online
    if (await isOnline()) {
      await trackingService.sync(trackingData);
    }
  }
};

const RouteOptimization = () => {
  const [visits, setVisits] = useState<Visit[]>([]);
  const [optimizedRoute, setOptimizedRoute] = useState(null);
  
  const optimizeRoute = async () => {
    const currentLocation = await getCurrentLocation();
    
    // Get optimal visit order
    const route = await routeService.optimize({
      origin: currentLocation,
      destinations: visits.map(v => v.location),
      returnToOrigin: true
    });
    
    setOptimizedRoute(route);
  };
  
  return (
    <MapView style={styles.map}>
      {optimizedRoute && (
        <Polyline
          coordinates={optimizedRoute.coordinates}
          strokeColor="#007AFF"
          strokeWidth={3}
        />
      )}
      {visits.map((visit, index) => (
        <Marker
          key={visit.id}
          coordinate={visit.location}
          title={visit.memberName}
          description={visit.purpose}
        >
          <View style={styles.markerLabel}>
            <Text>{index + 1}</Text>
          </View>
        </Marker>
      ))}
    </MapView>
  );
};
```

### Lead Management

```typescript
interface Lead {
  id: string;
  name: string;
  phone: string;
  email?: string;
  source: 'referral' | 'cold' | 'campaign';
  status: 'new' | 'contacted' | 'qualified' | 'converted' | 'lost';
  notes: string[];
  nextFollowUp?: Date;
}

const LeadManagement = () => {
  const [leads, setLeads] = useState<Lead[]>([]);
  
  const addLead = async (leadData: NewLead) => {
    const lead = {
      ...leadData,
      id: generateId(),
      createdBy: currentAgent.id,
      createdAt: new Date(),
      location: await getCurrentLocation()
    };
    
    await realmService.saveLead(lead);
    setLeads([...leads, lead]);
    
    // Schedule follow-up reminder
    if (lead.nextFollowUp) {
      await scheduleNotification({
        title: 'Follow-up Reminder',
        body: `Follow up with ${lead.name}`,
        fireDate: lead.nextFollowUp
      });
    }
  };
  
  const convertLead = async (leadId: string) => {
    const lead = leads.find(l => l.id === leadId);
    
    // Navigate to enrollment with pre-filled data
    navigation.navigate('Enrollment', {
      prefilledData: {
        name: lead.name,
        phone: lead.phone,
        email: lead.email
      }
    });
    
    // Update lead status
    await updateLeadStatus(leadId, 'converted');
  };
  
  return (
    <View>
      <LeadStats leads={leads} />
      <LeadList 
        leads={leads}
        onAddNote={addNote}
        onScheduleFollowUp={scheduleFollowUp}
        onConvert={convertLead}
      />
      <FAB onPress={() => navigation.navigate('AddLead')} />
    </View>
  );
};
```

### Offline Data Sync

```typescript
import Realm from 'realm';
import NetInfo from '@react-native-community/netinfo';

const OfflineSyncService = {
  realm: null,
  syncInProgress: false,
  
  initialize: async () => {
    this.realm = await Realm.open({
      schema: [EnrollmentSchema, PaymentSchema, ClaimSchema, LeadSchema],
      schemaVersion: 1,
      encryptionKey: generateEncryptionKey()
    });
    
    // Listen for connectivity changes
    NetInfo.addEventListener(state => {
      if (state.isConnected && !this.syncInProgress) {
        this.syncAll();
      }
    });
  },
  
  syncAll: async () => {
    this.syncInProgress = true;
    
    try {
      await this.syncEnrollments();
      await this.syncPayments();
      await this.syncClaims();
      await this.syncLeads();
      await this.syncTracking();
    } finally {
      this.syncInProgress = false;
    }
  },
  
  syncEnrollments: async () => {
    const pendingEnrollments = this.realm
      .objects('Enrollment')
      .filtered('synced = false');
    
    for (const enrollment of pendingEnrollments) {
      try {
        const response = await enrollmentService.submit(enrollment);
        
        this.realm.write(() => {
          enrollment.synced = true;
          enrollment.memberNumber = response.memberNumber;
          enrollment.syncedAt = new Date();
        });
      } catch (error) {
        console.log(`Failed to sync enrollment ${enrollment.id}`);
      }
    }
  }
};
```

### Commission Tracking

```typescript
const CommissionDashboard = () => {
  const [commissions, setCommissions] = useState({
    currentMonth: 0,
    pending: 0,
    paid: 0,
    breakdown: []
  });
  
  useEffect(() => {
    loadCommissions();
  }, []);
  
  const loadCommissions = async () => {
    const data = await commissionService.getAgentCommissions({
      agentId: currentAgent.id,
      period: getCurrentMonth()
    });
    
    setCommissions(data);
  };
  
  return (
    <ScrollView>
      <CommissionSummaryCard commissions={commissions} />
      <CommissionChart data={commissions.breakdown} />
      <CommissionDetailsList items={commissions.breakdown} />
      <PayoutHistory payouts={commissions.payoutHistory} />
    </ScrollView>
  );
};
```

## State Management (MobX)

### Store Structure

```typescript
class RootStore {
  authStore: AuthStore;
  agentStore: AgentStore;
  enrollmentStore: EnrollmentStore;
  paymentStore: PaymentStore;
  leadStore: LeadStore;
  taskStore: TaskStore;
  syncStore: SyncStore;
  
  constructor() {
    this.authStore = new AuthStore(this);
    this.agentStore = new AgentStore(this);
    this.enrollmentStore = new EnrollmentStore(this);
    this.paymentStore = new PaymentStore(this);
    this.leadStore = new LeadStore(this);
    this.taskStore = new TaskStore(this);
    this.syncStore = new SyncStore(this);
  }
}

class AgentStore {
  @observable currentAgent: Agent = null;
  @observable territory: Territory = null;
  @observable performance: Performance = null;
  
  @action
  setAgent(agent: Agent) {
    this.currentAgent = agent;
  }
  
  @computed
  get monthlyTarget() {
    return this.performance?.targets?.monthly || 0;
  }
  
  @computed
  get achievementRate() {
    return (this.performance?.achieved / this.monthlyTarget) * 100;
  }
}
```

## Testing

### Unit Testing

```typescript
// __tests__/EnrollmentValidation.test.ts
import { validateEnrollment } from '../src/utils/validation';

describe('Enrollment Validation', () => {
  it('should validate required fields', () => {
    const enrollment = {
      name: '',
      idNumber: '',
      phone: ''
    };
    
    const errors = validateEnrollment(enrollment);
    
    expect(errors).toContain('Name is required');
    expect(errors).toContain('ID number is required');
    expect(errors).toContain('Phone is required');
  });
  
  it('should validate ID number format', () => {
    const enrollment = {
      idNumber: '123' // Invalid KTP
    };
    
    const errors = validateEnrollment(enrollment);
    
    expect(errors).toContain('Invalid ID number format');
  });
});
```

### E2E Testing

```javascript
// e2e/agentFlow.e2e.js
describe('Agent Daily Flow', () => {
  beforeAll(async () => {
    await device.launchApp();
    await loginAsAgent('AGENT001');
  });
  
  it('should complete member enrollment', async () => {
    await element(by.id('new-enrollment')).tap();
    
    // Scan KTP
    await element(by.id('scan-ktp')).tap();
    await device.mockCamera('ktp_sample.jpg');
    
    // Verify OCR filled fields
    await expect(element(by.id('name-input'))).toHaveText('John Doe');
    
    // Select plan
    await element(by.id('select-plan')).tap();
    await element(by.text('Basic Plan')).tap();
    
    // Submit
    await element(by.id('submit-enrollment')).tap();
    await expect(element(by.text('Enrollment successful'))).toBeVisible();
  });
});
```

## Performance Optimization

### Realm Database Optimization

```typescript
const RealmConfig = {
  schema: schemas,
  schemaVersion: 2,
  migration: (oldRealm, newRealm) => {
    // Handle migrations
  },
  shouldCompactOnLaunch: (totalBytes, usedBytes) => {
    const oneHundredMB = 100 * 1024 * 1024;
    return totalBytes > oneHundredMB && usedBytes / totalBytes < 0.5;
  }
};
```

### Image Compression

```typescript
import ImageResizer from 'react-native-image-resizer';

const compressImage = async (imageUri: string) => {
  const resized = await ImageResizer.createResizedImage(
    imageUri,
    1024, // maxWidth
    1024, // maxHeight
    'JPEG',
    80, // quality
    0 // rotation
  );
  
  return resized.uri;
};
```

## Security

### Agent Authentication

```typescript
const AgentAuth = {
  login: async (agentId: string, pin: string) => {
    const hashedPin = await hashPin(pin);
    
    const response = await authService.agentLogin({
      agentId,
      pin: hashedPin,
      deviceId: await getDeviceId(),
      location: await getCurrentLocation()
    });
    
    // Save token securely
    await Keychain.setInternetCredentials(
      'agent-app',
      agentId,
      response.token
    );
    
    return response;
  },
  
  setupBiometric: async () => {
    const biometryType = await LocalAuthentication.hasHardwareAsync();
    
    if (biometryType) {
      await LocalAuthentication.authenticateAsync({
        promptMessage: 'Setup biometric login'
      });
      
      await AsyncStorage.setItem('biometric_enabled', 'true');
    }
  }
};
```

## Build & Release

### Production Build

```bash
# iOS
cd ios
xcodebuild -workspace FieldAgentApp.xcworkspace \
  -scheme FieldAgentApp \
  -configuration Release \
  -archivePath ../build/FieldAgentApp.xcarchive \
  archive

# Android
cd android
./gradlew assembleRelease
./gradlew bundleRelease
```

## Monitoring

### Agent Activity Monitoring

```typescript
const ActivityTracker = {
  trackActivity: async (activity: AgentActivity) => {
    await mixpanel.track(activity.type, {
      agentId: currentAgent.id,
      territory: currentAgent.territory,
      timestamp: new Date(),
      location: await getCurrentLocation(),
      ...activity.data
    });
  },
  
  trackPerformance: async () => {
    const metrics = {
      enrollmentsToday: await getEnrollmentCount('today'),
      premiumsCollected: await getPremiumTotal('today'),
      leadsGenerated: await getLeadCount('today'),
      visitsCompleted: await getVisitCount('today')
    };
    
    await mixpanel.people.set(currentAgent.id, metrics);
  }
};
```

## Troubleshooting

### Common Issues

1. **Realm sync conflicts**
   ```bash
   npm run realm:reset
   npm run realm:migrate
   ```

2. **GPS tracking not working**
   - Check location permissions
   - Ensure background location is enabled
   - Check battery optimization settings

3. **Offline data loss**
   - Check Realm encryption key
   - Verify database integrity
   - Review sync logs

## Support

- **Field Support**: field-support@claims-askes.com
- **Technical Issues**: mobile-support@claims-askes.com
- **Training**: training@claims-askes.com
- **Documentation**: [Full docs](../../../docs)

## License

Proprietary - All rights reserved