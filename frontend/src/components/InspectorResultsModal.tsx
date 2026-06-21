import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button,
  Box, Typography, Tab, Tabs, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Paper, Chip, CircularProgress,
  IconButton, Divider, Alert
} from '@mui/material';
import {
  Close as CloseIcon,
  FindInPage as InspectorIcon,
  Storage as SchemaIcon,
  Map as GeoIcon,
  BarChart as StatsIcon,
  TableChart as SampleIcon,
  Dashboard as OverviewIcon,
  Map as MapIcon
} from '@mui/icons-material';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import wellknown from 'wellknown';

interface InspectorResultsModalProps {
  open: boolean;
  onClose: () => void;
  executionId: string | null;
  nodeKey: string | null;
}

const MapBounds: React.FC<{ bounds: any }> = ({ bounds }) => {
  const map = useMap();
  useEffect(() => {
    if (bounds && bounds.miny !== undefined && bounds.maxx !== undefined) {
      map.fitBounds([
        [bounds.miny, bounds.minx],
        [bounds.maxy, bounds.maxx]
      ], { padding: [20, 20] });
    }
  }, [bounds, map]);
  return null;
};

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
    </div>
  );
}

const InspectorResultsModal: React.FC<InspectorResultsModalProps> = ({
  open, onClose, executionId, nodeKey
}) => {
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tabIndex, setTabIndex] = useState(0);

  useEffect(() => {
    if (open && executionId && nodeKey) {
      setLoading(true);
      setError(null);
      setReport(null);

      const token = localStorage.getItem('token') || '';
      fetch(`/api/executions/${executionId}/inspection/${nodeKey}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => {
          if (!res.ok) throw new Error(`Failed to load report (${res.status})`);
          return res.json();
        })
        .then(data => {
          setReport(data);
          setLoading(false);
        })
        .catch(err => {
          setError(err.message);
          setLoading(false);
        });
    }
  }, [open, executionId, nodeKey]);

  const cellSx = { fontSize: '12px', py: 0.8, px: 1.5, fontFamily: 'monospace' };
  const headerSx = { ...cellSx, fontWeight: 700, backgroundColor: '#f1f5f9', color: '#334155' };

  const renderOverview = () => {
    if (!report?.overview) return null;
    const ov = report.overview;
    const items = [
      { label: 'Data Type', value: ov.data_type },
      { label: 'Row Count', value: ov.row_count?.toLocaleString() },
      { label: 'Column Count', value: ov.column_count },
      { label: 'Memory Usage', value: `${ov.memory_usage_mb} MB` },
      { label: 'GeoDataFrame', value: ov.is_geodataframe ? 'Yes' : 'No' },
    ];
    return (
      <Box>
        <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2 }}>
          <Table size="small">
            <TableBody>
              {items.map(item => (
                <TableRow key={item.label}>
                  <TableCell sx={{ ...cellSx, fontWeight: 600, width: 180, color: '#475569' }}>{item.label}</TableCell>
                  <TableCell sx={cellSx}>{item.value}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    );
  };

  const renderSchema = () => {
    if (!report?.schema) return null;
    return (
      <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={headerSx}>Column</TableCell>
              <TableCell sx={headerSx}>Data Type</TableCell>
              <TableCell sx={headerSx} align="right">Non-Null</TableCell>
              <TableCell sx={headerSx} align="right">Null</TableCell>
              <TableCell sx={headerSx} align="right">Null %</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {report.schema.map((col: any, idx: number) => (
              <TableRow key={idx} sx={{ '&:nth-of-type(odd)': { backgroundColor: '#fafbfc' } }}>
                <TableCell sx={{ ...cellSx, fontWeight: 600, color: '#1e293b' }}>{col.column}</TableCell>
                <TableCell sx={cellSx}>
                  <Chip label={col.dtype} size="small" sx={{ fontSize: '10px', height: 20, fontFamily: 'monospace' }} />
                </TableCell>
                <TableCell sx={cellSx} align="right">{col.non_null_count}</TableCell>
                <TableCell sx={{ ...cellSx, color: col.null_count > 0 ? '#ef4444' : '#22c55e' }} align="right">
                  {col.null_count}
                </TableCell>
                <TableCell sx={{ ...cellSx, color: col.null_pct > 0 ? '#ef4444' : '#22c55e' }} align="right">
                  {col.null_pct}%
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  const renderGeometry = () => {
    if (!report?.geometry) {
      return <Alert severity="info" sx={{ borderRadius: 2 }}>No geometry information — this is a standard DataFrame.</Alert>;
    }
    const geo = report.geometry;
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2 }}>
          <Table size="small">
            <TableBody>
              <TableRow>
                <TableCell sx={{ ...cellSx, fontWeight: 600, width: 180 }}>Geometry Column</TableCell>
                <TableCell sx={cellSx}>{geo.geometry_column || 'N/A'}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ ...cellSx, fontWeight: 600 }}>CRS</TableCell>
                <TableCell sx={cellSx}>{geo.crs_name || geo.crs || 'Not set'}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ ...cellSx, fontWeight: 600 }}>EPSG Code</TableCell>
                <TableCell sx={cellSx}>{geo.crs_epsg ?? 'N/A'}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ ...cellSx, fontWeight: 600 }}>Features with Geometry</TableCell>
                <TableCell sx={cellSx}>{geo.total_with_geometry}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell sx={{ ...cellSx, fontWeight: 600 }}>Empty Geometries</TableCell>
                <TableCell sx={cellSx}>{geo.empty_geometry_count}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>

        {geo.geometry_types && Object.keys(geo.geometry_types).length > 0 && (
          <Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1, fontSize: '12px' }}>Geometry Types</Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {Object.entries(geo.geometry_types).map(([gtype, count]: [string, any]) => (
                <Chip key={gtype} label={`${gtype}: ${count}`} size="small"
                  sx={{ fontFamily: 'monospace', fontSize: '11px', backgroundColor: '#ecfeff', color: '#0891b2', fontWeight: 600 }}
                />
              ))}
            </Box>
          </Box>
        )}

        {geo.bounding_box && (
          <Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1, fontSize: '12px' }}>Bounding Box</Typography>
            <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2 }}>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell sx={{ ...cellSx, fontWeight: 600 }}>Min X (West)</TableCell>
                    <TableCell sx={cellSx}>{geo.bounding_box.minx}</TableCell>
                    <TableCell sx={{ ...cellSx, fontWeight: 600 }}>Max X (East)</TableCell>
                    <TableCell sx={cellSx}>{geo.bounding_box.maxx}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell sx={{ ...cellSx, fontWeight: 600 }}>Min Y (South)</TableCell>
                    <TableCell sx={cellSx}>{geo.bounding_box.miny}</TableCell>
                    <TableCell sx={{ ...cellSx, fontWeight: 600 }}>Max Y (North)</TableCell>
                    <TableCell sx={cellSx}>{geo.bounding_box.maxy}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}
      </Box>
    );
  };

  const renderStatistics = () => {
    if (!report?.statistics) {
      return <Alert severity="info" sx={{ borderRadius: 2 }}>Statistics were not computed for this inspection.</Alert>;
    }
    const stats = report.statistics;
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {stats.numeric?.length > 0 && (
          <Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1, fontSize: '12px', color: '#475569' }}>
              Numeric Columns
            </Typography>
            <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={headerSx}>Column</TableCell>
                    <TableCell sx={headerSx} align="right">Min</TableCell>
                    <TableCell sx={headerSx} align="right">Max</TableCell>
                    <TableCell sx={headerSx} align="right">Mean</TableCell>
                    <TableCell sx={headerSx} align="right">Std</TableCell>
                    <TableCell sx={headerSx} align="right">Median</TableCell>
                    <TableCell sx={headerSx} align="right">25th</TableCell>
                    <TableCell sx={headerSx} align="right">75th</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {stats.numeric.map((s: any, idx: number) => (
                    <TableRow key={idx} sx={{ '&:nth-of-type(odd)': { backgroundColor: '#fafbfc' } }}>
                      <TableCell sx={{ ...cellSx, fontWeight: 600 }}>{s.column}</TableCell>
                      <TableCell sx={cellSx} align="right">{s.min ?? '-'}</TableCell>
                      <TableCell sx={cellSx} align="right">{s.max ?? '-'}</TableCell>
                      <TableCell sx={cellSx} align="right">{s.mean ?? '-'}</TableCell>
                      <TableCell sx={cellSx} align="right">{s.std ?? '-'}</TableCell>
                      <TableCell sx={cellSx} align="right">{s.median ?? '-'}</TableCell>
                      <TableCell sx={cellSx} align="right">{s['25th_pct'] ?? '-'}</TableCell>
                      <TableCell sx={cellSx} align="right">{s['75th_pct'] ?? '-'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {stats.categorical?.length > 0 && (
          <Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1, fontSize: '12px', color: '#475569' }}>
              Categorical Columns
            </Typography>
            <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={headerSx}>Column</TableCell>
                    <TableCell sx={headerSx} align="right">Unique Values</TableCell>
                    <TableCell sx={headerSx}>Top Values</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {stats.categorical.map((s: any, idx: number) => (
                    <TableRow key={idx} sx={{ '&:nth-of-type(odd)': { backgroundColor: '#fafbfc' } }}>
                      <TableCell sx={{ ...cellSx, fontWeight: 600 }}>{s.column}</TableCell>
                      <TableCell sx={cellSx} align="right">{s.unique_count}</TableCell>
                      <TableCell sx={cellSx}>
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                          {Object.entries(s.top_values || {}).map(([val, cnt]: [string, any]) => (
                            <Chip key={val} label={`${val} (${cnt})`} size="small"
                              sx={{ fontSize: '9px', height: 18, fontFamily: 'monospace' }}
                            />
                          ))}
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}
      </Box>
    );
  };

  const renderSampleData = () => {
    if (!report?.sample_data) return null;
    const sample = report.sample_data;
    const columns: string[] = sample.columns || [];

    const renderTable = (rows: any[], title: string) => (
      <Box>
        <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1, fontSize: '12px', color: '#475569' }}>
          {title} ({rows.length} rows)
        </Typography>
        <TableContainer component={Paper} variant="outlined" sx={{ borderRadius: 2, maxHeight: 300 }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                {columns.map(col => (
                  <TableCell key={col} sx={headerSx}>{col}</TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row: any, rIdx: number) => (
                <TableRow key={rIdx} sx={{ '&:nth-of-type(odd)': { backgroundColor: '#fafbfc' } }}>
                  {columns.map(col => (
                    <TableCell key={col} sx={{ ...cellSx, maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {row[col] !== null && row[col] !== undefined ? String(row[col]) : <em style={{ color: '#94a3b8' }}>null</em>}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    );

    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {sample.head?.length > 0 && renderTable(sample.head, 'Head (First Rows)')}
        {sample.tail?.length > 0 && renderTable(sample.tail, 'Tail (Last Rows)')}
      </Box>
    );
  };

  const renderMapView = () => {
    if (!report?.geometry) {
      return <Alert severity="info" sx={{ borderRadius: 2 }}>No geometry information available to display on map.</Alert>;
    }
    
    const geo = report.geometry;
    const sample = report.sample_data;
    const geomCol = geo.geometry_column;
    
    if (!geomCol || (!sample?.head && !sample?.tail)) {
       return <Alert severity="warning">No sample geometry data available to display.</Alert>;
    }
    
    // Combine sample data and convert WKT to GeoJSON
    const allSampleRows = [...(sample.head || []), ...(sample.tail || [])];
    const geoJsonFeatures = allSampleRows.map((row: any) => {
      const wkt = row[geomCol];
      if (!wkt) return null;
      try {
        const geometry = wellknown.parse(wkt);
        if (!geometry) return null;
        return {
          type: "Feature",
          geometry: geometry,
          properties: row
        };
      } catch (e) {
        return null;
      }
    }).filter(f => f !== null);
    
    const featureCollection: any = {
      type: "FeatureCollection",
      features: geoJsonFeatures
    };
    
    // Default center to (0,0) if no bounding box
    const center: [number, number] = geo.bounding_box ? 
      [(geo.bounding_box.miny + geo.bounding_box.maxy) / 2, (geo.bounding_box.minx + geo.bounding_box.maxx) / 2] : 
      [0, 0];
      
    return (
      <Box sx={{ height: 400, width: '100%', borderRadius: 2, overflow: 'hidden', border: '1px solid #e2e8f0' }}>
        <MapContainer center={center} zoom={4} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {geo.bounding_box && <MapBounds bounds={geo.bounding_box} />}
          {geoJsonFeatures.length > 0 && (
            <GeoJSON 
              data={featureCollection} 
              style={{ color: '#0891b2', weight: 2, fillColor: '#06b6d4', fillOpacity: 0.4 }}
              onEachFeature={(feature, layer) => {
                const props = feature.properties;
                // Create a popup string with properties
                let popupContent = '<div style="max-height: 200px; overflow-y: auto;">';
                for (const [key, val] of Object.entries(props)) {
                  if (key !== geomCol) {
                    popupContent += `<strong>${key}</strong>: ${val}<br/>`;
                  }
                }
                popupContent += '</div>';
                layer.bindPopup(popupContent);
              }}
            />
          )}
        </MapContainer>
        <Typography variant="caption" sx={{ mt: 1, display: 'block', color: 'text.secondary' }}>
          * Map displays geometries from sample data rows only. Bounding box represents the entire dataset.
        </Typography>
      </Box>
    );
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: { borderRadius: 3, maxHeight: '85vh' }
      }}
    >
      <DialogTitle sx={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        py: 2, px: 3, backgroundColor: '#ecfeff', borderBottom: '1px solid #e2e8f0'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <InspectorIcon sx={{ color: '#0891b2' }} />
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 800, color: '#0f172a', lineHeight: 1.2 }}>
              {report?.label || 'Inspection Report'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Node: {nodeKey} | Execution: {executionId?.slice(0, 8)}...
            </Typography>
          </Box>
        </Box>
        <IconButton onClick={onClose} size="small"><CloseIcon /></IconButton>
      </DialogTitle>

      <DialogContent sx={{ p: 0 }}>
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 200 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Box sx={{ p: 3 }}>
            <Alert severity="warning" sx={{ borderRadius: 2 }}>
              {error}. Execute the pipeline first to generate an inspection report.
            </Alert>
          </Box>
        )}

        {report && !loading && (
          <Box>
            <Box sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}>
              <Tabs value={tabIndex} onChange={(_, v) => setTabIndex(v)}
                sx={{ '& .MuiTab-root': { fontSize: '12px', fontWeight: 600, textTransform: 'none', minHeight: 42 } }}
              >
                <Tab icon={<OverviewIcon sx={{ fontSize: 16 }} />} iconPosition="start" label="Overview" />
                <Tab icon={<SchemaIcon sx={{ fontSize: 16 }} />} iconPosition="start" label="Schema" />
                <Tab icon={<GeoIcon sx={{ fontSize: 16 }} />} iconPosition="start" label="Geometry" />
                <Tab icon={<StatsIcon sx={{ fontSize: 16 }} />} iconPosition="start" label="Statistics" />
                <Tab icon={<SampleIcon sx={{ fontSize: 16 }} />} iconPosition="start" label="Sample Data" />
                <Tab icon={<MapIcon sx={{ fontSize: 16 }} />} iconPosition="start" label="Map View" />
              </Tabs>
            </Box>
            <Box sx={{ p: 3 }}>
              <TabPanel value={tabIndex} index={0}>{renderOverview()}</TabPanel>
              <TabPanel value={tabIndex} index={1}>{renderSchema()}</TabPanel>
              <TabPanel value={tabIndex} index={2}>{renderGeometry()}</TabPanel>
              <TabPanel value={tabIndex} index={3}>{renderStatistics()}</TabPanel>
              <TabPanel value={tabIndex} index={4}>{renderSampleData()}</TabPanel>
              <TabPanel value={tabIndex} index={5}>{renderMapView()}</TabPanel>
            </Box>
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2, borderTop: '1px solid #e2e8f0', backgroundColor: '#f8fafc' }}>
        <Button onClick={onClose} variant="outlined" sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 600 }}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default InspectorResultsModal;
