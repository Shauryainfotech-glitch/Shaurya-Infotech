import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

export function PerformanceMetrics() {
  const metrics = [
    { name: "Prediction Accuracy", value: 94, color: "bg-green-600 dark:bg-green-500" },
    { name: "NLP Processing Speed", value: 87, color: "bg-blue-600 dark:bg-blue-500" },
    { name: "Risk Detection Rate", value: 91, color: "bg-purple-600 dark:bg-purple-500" },
    { name: "GPT-4 Response Time", value: 78, color: "bg-orange-600 dark:bg-orange-500" }
  ];

  const activities = [
    { name: "GPT-4 analysis completed", time: "2m ago", color: "bg-purple-500" },
    { name: "Risk assessment updated", time: "5m ago", color: "bg-green-500" },
    { name: "Market trends analyzed", time: "12m ago", color: "bg-blue-500" }
  ];

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle>AI Performance Metrics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {metrics.map((metric, index) => (
            <div key={index} className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">{metric.name}</span>
              <div className="flex items-center">
                <div className="w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mr-2">
                  <div className={`h-2 rounded-full ${metric.color}`} style={{width: `${metric.value}%`}}></div>
                </div>
                <span className="text-sm font-medium">
                  {index === 3 ? "1.2s" : `${metric.value}%`}
                </span>
              </div>
            </div>
          ))}
          
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-3">Latest AI Activities</h4>
            <div className="space-y-2">
              {activities.map((activity, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <div className="flex items-center">
                    <div className={`w-2 h-2 rounded-full mt-0.5 mr-2 ${activity.color}`}></div>
                    <span className="dark:text-gray-300">{activity.name}</span>
                  </div>
                  <span className="text-gray-500 dark:text-gray-400">{activity.time}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
