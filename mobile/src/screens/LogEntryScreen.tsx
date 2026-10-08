import React, { useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import * as endpoints from '../api/endpoints';
import type { ExerciseKey } from '../api/types';
import { useStandards } from '../context/StandardsContext';
import { Card, ErrorBanner, FormInput, PrimaryButton, Screen } from '../components/ui';
import { colors } from '../theme/colors';
import type { AppStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<AppStackParamList, 'LogEntry'>;

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

export default function LogEntryScreen({ navigation, route }: Props) {
  const editingEntry = route.params?.editingEntry;
  const { data: standardsData, isLoading: standardsLoading, error: standardsError } = useStandards();

  const [exercise, setExercise] = useState<ExerciseKey | null>(
    editingEntry?.exercise ?? null
  );
  const [value, setValue] = useState(
    editingEntry ? String(editingEntry.display_value) : ''
  );
  const [entryDate, setEntryDate] = useState(editingEntry?.entry_date ?? todayIso());
  const [notes, setNotes] = useState(editingEntry?.notes ?? '');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const selectedStd = exercise && standardsData ? standardsData.standards[exercise] : null;

  const onSubmit = async () => {
    setError(null);
    if (!exercise) {
      setError('Choose an exercise.');
      return;
    }
    if (!value.trim()) {
      setError('Enter a value.');
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        exercise,
        value: value.trim(),
        entry_date: entryDate || undefined,
        notes: notes.trim(),
      };
      if (editingEntry) {
        await endpoints.updateEntry(editingEntry.id, payload);
      } else {
        await endpoints.createEntry(payload);
      }
      navigation.goBack();
    } catch (e: any) {
      setError(e.message ?? 'Could not save this entry.');
    } finally {
      setSubmitting(false);
    }
  };

  if (standardsLoading) {
    return (
      <Screen>
        <ActivityIndicator color={colors.primary} style={styles.loader} />
      </Screen>
    );
  }

  return (
    <Screen>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.title}>{editingEntry ? 'Edit entry' : 'Log a result'}</Text>

        <ErrorBanner message={error ?? standardsError} />

        <Text style={styles.sectionLabel}>Exercise</Text>
        <View style={styles.chipRow}>
          {standardsData?.exercise_order.map((key) => {
            const std = standardsData.standards[key];
            const selected = exercise === key;
            return (
              <Pressable
                key={key}
                onPress={() => setExercise(key)}
                style={[styles.chip, selected && styles.chipSelected]}
              >
                <Text style={[styles.chipText, selected && styles.chipTextSelected]}>
                  {std.label}
                </Text>
              </Pressable>
            );
          })}
        </View>

        <FormInput
          label={
            selectedStd?.unit === 'time'
              ? 'Time (mm:ss, e.g. 9:45)'
              : 'Reps'
          }
          value={value}
          onChangeText={setValue}
          placeholder={selectedStd?.unit === 'time' ? '9:45' : '65'}
          keyboardType={selectedStd?.unit === 'time' ? 'default' : 'numeric'}
        />

        <FormInput
          label="Date (YYYY-MM-DD)"
          value={entryDate}
          onChangeText={setEntryDate}
          placeholder={todayIso()}
        />

        <FormInput
          label="Notes (optional)"
          value={notes}
          onChangeText={setNotes}
          placeholder="How did it feel?"
          multiline
        />

        {selectedStd ? (
          <Card style={styles.standardCard}>
            <Text style={styles.standardTitle}>Standard for {selectedStd.label}</Text>
            <Text style={styles.standardRow}>Minimum: {selectedStd.min_display}</Text>
            <Text style={styles.standardRow}>Competitive: {selectedStd.competitive_display}</Text>
            <Text style={styles.standardRow}>Max: {selectedStd.max_display}</Text>
          </Card>
        ) : null}

        <View style={styles.spacer} />
        <PrimaryButton
          title={editingEntry ? 'Save changes' : 'Log entry'}
          onPress={onSubmit}
          loading={submitting}
        />
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  content: { padding: 20, paddingBottom: 60 },
  loader: { marginTop: 60 },
  title: { fontSize: 24, fontWeight: '800', color: colors.text, marginBottom: 18 },
  sectionLabel: { color: colors.textMuted, fontSize: 13, fontWeight: '600', marginBottom: 8 },
  chipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 16 },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 9,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surfaceAlt,
  },
  chipSelected: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  chipText: { color: colors.textMuted, fontSize: 13, fontWeight: '600' },
  chipTextSelected: { color: '#fff' },
  standardCard: { marginTop: 4, marginBottom: 16 },
  standardTitle: { color: colors.text, fontWeight: '700', marginBottom: 6 },
  standardRow: { color: colors.textMuted, fontSize: 13, marginTop: 2 },
  spacer: { height: 6 },
});
