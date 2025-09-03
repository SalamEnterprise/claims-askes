/**
 * Main Pricing Configuration Form Component
 * Replicates the Excel-based UI for group health insurance setup
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Grid,
  Paper,
  TextField,
  Typography,
  Button,
  Divider,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Select,
  MenuItem,
  InputLabel,
  Alert,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
  InputAdornment,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import {
  Save as SaveIcon,
  Calculate as CalculateIcon,
  Send as SendIcon,
  People as PeopleIcon,
  AttachMoney as MoneyIcon,
  Info as InfoIcon,
  CloudUpload as UploadIcon,
} from '@mui/icons-material';
import { format, addYears } from 'date-fns';

import BenefitSelectionMatrix from './BenefitSelectionMatrix';
import TCFactorConfiguration from './TCFactorConfiguration';
import MemberManagement from './MemberManagement';
import PremiumCalculation from './PremiumCalculation';
import { usePricingApi } from '../../hooks/usePricingApi';
import { formatCurrency } from '../../utils/formatters';

interface PricingConfigurationFormProps {
  configId?: string;
  onSave?: (configId: string) => void;
  onSubmit?: (configId: string) => void;
}

interface FormData {
  companyName: string;
  industryType: string;
  participantCount: number;
  classCount: number;
  coverageStart: Date;
  coverageEnd: Date;
  pricingMethod: string;
  distributionChannel: string;
  pricingOfficer: string;
}

const PricingConfigurationForm: React.FC<PricingConfigurationFormProps> = ({
  configId,
  onSave,
  onSubmit,
}) => {
  // State management
  const [activeTab, setActiveTab] = useState(0);
  const [formData, setFormData] = useState<FormData>({
    companyName: '',
    industryType: '',
    participantCount: 10,
    classCount: 2,
    coverageStart: new Date(),
    coverageEnd: addYears(new Date(), 1),
    pricingMethod: 'FULLY_EXPERIENCED',
    distributionChannel: 'Corporate Bancassurance 1',
    pricingOfficer: '',
  });

  const [benefitSelections, setBenefitSelections] = useState({
    INPATIENT: true,
    OUTPATIENT: true,
    DENTAL: false,
    MATERNITY: false,
    OPTICAL: false,
    ASO: false,
  });

  const [tcFactors, setTcFactors] = useState({});
  const [members, setMembers] = useState([]);
  const [premiumData, setPremiumData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved'>('idle');

  const {
    createConfiguration,
    updateConfiguration,
    toggleBenefit,
    updateTCFactor,
    calculatePremium,
    addMember,
    importMembers,
    submitForApproval,
  } = usePricingApi();

  // Load existing configuration if configId provided
  useEffect(() => {
    if (configId) {
      loadConfiguration(configId);
    }
  }, [configId]);

  const loadConfiguration = async (id: string) => {
    setLoading(true);
    try {
      // Load configuration data
      // Implementation would fetch from API
      setLoading(false);
    } catch (err) {
      setError('Failed to load configuration');
      setLoading(false);
    }
  };

  // Auto-save functionality
  useEffect(() => {
    const autoSaveTimer = setTimeout(() => {
      if (configId && saveStatus === 'idle') {
        handleAutoSave();
      }
    }, 3000);

    return () => clearTimeout(autoSaveTimer);
  }, [formData, benefitSelections, tcFactors]);

  const handleAutoSave = async () => {
    if (!configId) return;
    
    setSaveStatus('saving');
    try {
      await updateConfiguration(configId, {
        ...formData,
        benefitSelections,
        tcFactors,
      });
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 2000);
    } catch (err) {
      console.error('Auto-save failed:', err);
      setSaveStatus('idle');
    }
  };

  // Form handlers
  const handleFormChange = (field: keyof FormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleBenefitToggle = async (category: string, selected: boolean) => {
    setBenefitSelections(prev => ({
      ...prev,
      [category]: selected,
    }));

    if (configId) {
      try {
        const result = await toggleBenefit(configId, category, selected);
        if (result.premiumUpdate) {
          setPremiumData(result.premiumUpdate);
        }
      } catch (err) {
        setError(`Failed to update benefit: ${err.message}`);
      }
    }
  };

  const handleTCFactorChange = async (factorCode: string, optionValue: string) => {
    setTcFactors(prev => ({
      ...prev,
      [factorCode]: optionValue,
    }));

    if (configId) {
      try {
        const result = await updateTCFactor(configId, factorCode, optionValue);
        if (result.premiumUpdate) {
          setPremiumData(result.premiumUpdate);
        }
      } catch (err) {
        setError(`Failed to update factor: ${err.message}`);
      }
    }
  };

  const handleCalculatePremium = async () => {
    if (!configId) {
      setError('Please save configuration first');
      return;
    }

    setLoading(true);
    try {
      const result = await calculatePremium(configId);
      setPremiumData(result);
      setActiveTab(4); // Switch to premium tab
    } catch (err) {
      setError(`Calculation failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveConfiguration = async () => {
    setLoading(true);
    setError(null);

    try {
      let currentConfigId = configId;
      
      if (!currentConfigId) {
        // Create new configuration
        const result = await createConfiguration(formData);
        currentConfigId = result.configId;
      } else {
        // Update existing
        await updateConfiguration(currentConfigId, formData);
      }

      if (onSave) {
        onSave(currentConfigId);
      }
      
      setError(null);
    } catch (err) {
      setError(`Failed to save: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitForApproval = async () => {
    if (!configId) {
      setError('Configuration must be saved first');
      return;
    }

    setLoading(true);
    try {
      await submitForApproval(configId);
      if (onSubmit) {
        onSubmit(configId);
      }
    } catch (err) {
      setError(`Submission failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ width: '100%', bgcolor: 'background.paper' }}>
        {/* Header */}
        <Paper elevation={0} sx={{ p: 3, bgcolor: 'primary.main', color: 'white' }}>
          <Typography variant="h4" gutterBottom>
            Pricing Asuransi PROFESSIONAL GROUP HEALTH v4.3
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
            {saveStatus === 'saving' && (
              <Chip label="Saving..." size="small" color="warning" />
            )}
            {saveStatus === 'saved' && (
              <Chip label="Saved" size="small" color="success" />
            )}
            {configId && (
              <Chip label={`Config ID: ${configId.slice(0, 8)}...`} size="small" />
            )}
          </Box>
        </Paper>

        {/* Error/Loading States */}
        {loading && <LinearProgress />}
        {error && (
          <Alert severity="error" onClose={() => setError(null)} sx={{ m: 2 }}>
            {error}
          </Alert>
        )}

        {/* Main Content */}
        <Box sx={{ p: 3 }}>
          <Grid container spacing={3}>
            {/* Left Panel - Company Information */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Policy Configuration
                </Typography>
                <Divider sx={{ mb: 2 }} />

                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Calon Pemegang Polis"
                      value={formData.companyName}
                      onChange={(e) => handleFormChange('companyName', e.target.value)}
                      required
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <FormControl fullWidth>
                      <InputLabel>Bidang Usaha</InputLabel>
                      <Select
                        value={formData.industryType}
                        onChange={(e) => handleFormChange('industryType', e.target.value)}
                        label="Bidang Usaha"
                      >
                        <MenuItem value="Manufacturing">Manufacturing</MenuItem>
                        <MenuItem value="Services">Services</MenuItem>
                        <MenuItem value="Banking">Banking</MenuItem>
                        <MenuItem value="Retail">Retail</MenuItem>
                        <MenuItem value="Technology">Technology</MenuItem>
                        <MenuItem value="Healthcare">Healthcare</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      type="number"
                      label="Jumlah Peserta"
                      value={formData.participantCount}
                      onChange={(e) => handleFormChange('participantCount', parseInt(e.target.value))}
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <PeopleIcon />
                          </InputAdornment>
                        ),
                      }}
                    />
                  </Grid>

                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      type="number"
                      label="Jumlah Kelas"
                      value={formData.classCount}
                      onChange={(e) => handleFormChange('classCount', parseInt(e.target.value))}
                    />
                  </Grid>

                  <Grid item xs={6}>
                    <DatePicker
                      label="Masa Asuransi - Mulai"
                      value={formData.coverageStart}
                      onChange={(date) => handleFormChange('coverageStart', date)}
                      renderInput={(params) => <TextField {...params} fullWidth />}
                    />
                  </Grid>

                  <Grid item xs={6}>
                    <DatePicker
                      label="Masa Asuransi - Akhir"
                      value={formData.coverageEnd}
                      onChange={(date) => handleFormChange('coverageEnd', date)}
                      renderInput={(params) => <TextField {...params} fullWidth />}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <FormControl fullWidth>
                      <InputLabel>Distribusi Penjualan</InputLabel>
                      <Select
                        value={formData.distributionChannel}
                        onChange={(e) => handleFormChange('distributionChannel', e.target.value)}
                        label="Distribusi Penjualan"
                      >
                        <MenuItem value="Corporate Bancassurance 1">
                          Corporate Bancassurance 1
                        </MenuItem>
                        <MenuItem value="Open Market">Open Market</MenuItem>
                        <MenuItem value="Direct Sales">Direct Sales</MenuItem>
                        <MenuItem value="Agency">Agency</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Petugas Pricing"
                      value={formData.pricingOfficer}
                      onChange={(e) => handleFormChange('pricingOfficer', e.target.value)}
                    />
                  </Grid>
                </Grid>
              </Paper>
            </Grid>

            {/* Right Panel - Benefit Selection */}
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Jenis Benefit Tambahan
                </Typography>
                <Divider sx={{ mb: 2 }} />

                <BenefitSelectionMatrix
                  selections={benefitSelections}
                  onChange={handleBenefitToggle}
                />

                {/* Premium Summary Card */}
                {premiumData && (
                  <Paper elevation={3} sx={{ p: 2, mt: 3, bgcolor: 'warning.light' }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Estimated Premium
                    </Typography>
                    <Typography variant="h5">
                      {formatCurrency(premiumData.totalPremium)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Per Year ({formData.participantCount} participants)
                    </Typography>
                  </Paper>
                )}
              </Paper>
            </Grid>
          </Grid>

          {/* Tabs for Configuration Details */}
          <Paper sx={{ mt: 3 }}>
            <Tabs
              value={activeTab}
              onChange={(_, newValue) => setActiveTab(newValue)}
              indicatorColor="primary"
              textColor="primary"
            >
              <Tab label="General TC" />
              <Tab label="Benefit Configuration" />
              <Tab label="Members" />
              <Tab label="TC Factors" />
              <Tab label="Premium Calculation" />
            </Tabs>

            <Box sx={{ p: 3 }}>
              {activeTab === 0 && (
                <TCFactorConfiguration
                  category="GENERAL"
                  factors={tcFactors}
                  onChange={handleTCFactorChange}
                  configId={configId}
                />
              )}

              {activeTab === 1 && (
                <Box>
                  <TCFactorConfiguration
                    category="INPATIENT"
                    factors={tcFactors}
                    onChange={handleTCFactorChange}
                    configId={configId}
                  />
                  <Divider sx={{ my: 3 }} />
                  <TCFactorConfiguration
                    category="OUTPATIENT"
                    factors={tcFactors}
                    onChange={handleTCFactorChange}
                    configId={configId}
                  />
                </Box>
              )}

              {activeTab === 2 && (
                <MemberManagement
                  configId={configId}
                  participantCount={formData.participantCount}
                  onMembersUpdate={(newMembers) => setMembers(newMembers)}
                  onPremiumUpdate={(premium) => setPremiumData(premium)}
                />
              )}

              {activeTab === 3 && (
                <Box>
                  {benefitSelections.DENTAL && (
                    <TCFactorConfiguration
                      category="DENTAL"
                      factors={tcFactors}
                      onChange={handleTCFactorChange}
                      configId={configId}
                    />
                  )}
                  {benefitSelections.MATERNITY && (
                    <TCFactorConfiguration
                      category="MATERNITY"
                      factors={tcFactors}
                      onChange={handleTCFactorChange}
                      configId={configId}
                    />
                  )}
                </Box>
              )}

              {activeTab === 4 && (
                <PremiumCalculation
                  configId={configId}
                  premiumData={premiumData}
                  onCalculate={handleCalculatePremium}
                />
              )}
            </Box>
          </Paper>

          {/* Action Buttons */}
          <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
            <Button
              variant="outlined"
              startIcon={<SaveIcon />}
              onClick={handleSaveConfiguration}
              disabled={loading}
            >
              Save Draft
            </Button>

            <Button
              variant="contained"
              color="secondary"
              startIcon={<CalculateIcon />}
              onClick={handleCalculatePremium}
              disabled={!configId || loading}
            >
              Calculate Premium
            </Button>

            <Button
              variant="contained"
              color="primary"
              startIcon={<SendIcon />}
              onClick={handleSubmitForApproval}
              disabled={!configId || loading}
            >
              Submit for Approval
            </Button>
          </Box>
        </Box>
      </Box>
    </LocalizationProvider>
  );
};

export default PricingConfigurationForm;