import React, { useCallback, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

import * as endpoints from '../api/endpoints';
import type { LogEntry } from '../api/types';
import { Card, ErrorBanner, Screen, TextButton } from '../components/ui';
import { colors } from '../theme/colors';
import type { AppStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<AppStackParamList, 'History'>;

const PER_PAGE = 20;

export default function HistoryScreen({ navigation }: Props) {
  const [entries, setEntries] = useState<LogEntry[]>([]);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadFirstPage = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await endpoints.fetchEntries(1, PER_PAGE);
      setEntries(res.entries);
      setPage(1);
      setHasNext(res.has_next);
    } catch (e: any) {
      setError(e.message ?? 'Failed to load history.');
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadFirstPage();
    }, [loadFirstPage])
  );

  const loadMore = async () => {
    if (!hasNext || loadingMore) return;
    setLoadingMore(true);
    try {
      const nextPage = page + 1;
      const res = await endpoints.fetchEntries(nextPage, PER_PAGE);
      setEntries((prev) => [...prev, ...res.entries]);
      setPage(nextPage);
      setHasNext(res.has_next);
    } catch (e: any) {
      setError(e.message ?? 'Failed to load more entries.');
    } finally {
      setLoadingMore(false);
    }
  };

  const confirmDelete = (entry: LogEntry) => {
    Alert.alert('Delete entry?', `${entry.label} — ${entry.display_value}`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Delete',
        style: 'destructive',
        onPress: async () => {
          try {
            await endpoints.deleteEntry(entry.id);
            setEntries((prev) => prev.filter((e) => e.id !== entry.id));
          } catch (e: any) {
            setError(e.message ?? 'Failed to delete entry.');
          }
        },
      },
    ]);
  };

  return (
    <Screen>
      <View style={styles.header}>
        <Text style={styles.title}>History</Text>
      </View>

      <ErrorBanner message={error} />

      {loading ? (
        <ActivityIndicator color={colors.primary} style={styles.loader} />
      ) : (
        <FlatList
          data={entries}
          keyExtractor={(item) => String(item.id)}
          contentContainerStyle={styles.listContent}
          onEndReachedThreshold={0.4}
          onEndReached={loadMore}
          ListEmptyComponent={<Text style={styles.emptyText}>No entries logged yet.</Text>}
          ListFooterComponent={
            loadingMore ? <ActivityIndicator color={colors.primary} style={styles.footerLoader} /> : null
          }
          renderItem={({ item }) => (
            <Card style={styles.row}>
              <View style={styles.rowMain}>
                <Text style={styles.rowLabel}>{item.label}</Text>
                <Text style={styles.rowValue}>{item.display_value}</Text>
                <Text style={styles.rowDate}>
                  {item.entry_date}
                  {item.notes ? ` · ${item.notes}` : ''}
                </Text>
              </View>
              <View style={styles.rowActions}>
                <TextButton
                  title="Edit"
                  onPress={() => navigation.navigate('LogEntry', { editingEntry: item })}
                />
                <View style={styles.actionGap} />
                <TextButton title="Delete" color={colors.danger} onPress={() => confirmDelete(item)} />
              </View>
            </Card>
          )}
        />
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  header: { paddingHorizontal: 20, paddingTop: 10, paddingBottom: 6 },
  title: { fontSize: 24, fontWeight: '800', color: colors.text },
  loader: { marginTop: 40 },
  footerLoader: { marginVertical: 16 },
  listContent: { paddingHorizontal: 20, paddingBottom: 40 },
  emptyText: { color: colors.textMuted, textAlign: 'center', marginTop: 40 },
  row: {
    marginBottom: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  rowMain: { flex: 1, paddingRight: 12 },
  rowLabel: { color: colors.text, fontWeight: '700', fontSize: 14 },
  rowValue: { color: colors.text, fontSize: 18, fontWeight: '800', marginTop: 2 },
  rowDate: { color: colors.textMuted, fontSize: 12, marginTop: 4 },
  rowActions: { flexDirection: 'row', alignItems: 'center' },
  actionGap: { width: 14 },
});
