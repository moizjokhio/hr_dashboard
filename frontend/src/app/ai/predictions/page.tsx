"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

export default function PredictionsPage() {
  const [employeeId, setEmployeeId] = useState("");
  const [prediction, setPrediction] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handlePredict = async () => {
    if (!employeeId) return;
    setLoading(true);
    setError("");
    setPrediction(null);

    try {
      const response = await api.get(`/ai/predict/${employeeId}`);
      setPrediction(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to get prediction");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Attrition Risk Prediction</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Predict Employee Risk</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <Input 
              placeholder="Enter Employee ID" 
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
            />
            <Button onClick={handlePredict} disabled={loading}>
              {loading ? "Analyzing..." : "Predict"}
            </Button>
          </div>

          {error && <div className="text-red-500">{error}</div>}

          {prediction && (
            <div className="mt-6 p-4 border rounded-lg bg-slate-50">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold text-lg">Risk Score</h3>
                  <div className={`text-2xl font-bold ${prediction.risk_score > 0.5 ? 'text-red-600' : 'text-green-600'}`}>
                    {(prediction.risk_score * 100).toFixed(1)}%
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Main Factor</h3>
                  <div className="text-xl">{prediction.main_factor}</div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
