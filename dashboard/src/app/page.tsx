"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  
  const [selectedInterface, setSelectedInterface] = useState<string | null>(null);
  const [response, setResponse] = useState<any>(null);

  const handleInterfaceSelection = (value: string) => {
    setSelectedInterface(value);
    setResponse(null);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const endpoint = formData.get("endpoint") as string;
    
    // Here you would typically make an API call
    // For demonstration, we'll just set a mock response
    setResponse(`Mock response for ${selectedInterface} - ${endpoint}`);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">API Interface</h1>
      
      <Select onValueChange={handleInterfaceSelection}>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Select interface" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="database">Database</SelectItem>
          <SelectItem value="drive">Drive</SelectItem>
          <SelectItem value="wallet">Wallet</SelectItem>
        </SelectContent>
      </Select>

      {selectedInterface && (
        <Card className="mt-4">
          <CardHeader>
            <CardTitle>{selectedInterface.charAt(0).toUpperCase() + selectedInterface.slice(1)} Interface</CardTitle>
            <CardDescription>Select an endpoint and provide necessary data</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Select name="endpoint">
                <SelectTrigger>
                  <SelectValue placeholder="Select endpoint" />
                </SelectTrigger>
                <SelectContent>
                  {selectedInterface === "database" && (
                    <>
                      <SelectItem value="query">Query</SelectItem>
                      <SelectItem value="update">Update</SelectItem>
                      <SelectItem value="insert">Insert</SelectItem>
                      <SelectItem value="delete">Delete</SelectItem>
                    </>
                  )}
                  {selectedInterface === "drive" && (
                    <>
                      <SelectItem value="query_file">Query and download file</SelectItem>
                      <SelectItem value="query_id">Query file by ID</SelectItem>
                      <SelectItem value="query_files">Query files in folder</SelectItem>
                    </>
                  )}
                  {selectedInterface === "wallet" && (
                    <SelectItem value="generateStatements">Generate monthly statements</SelectItem>
                  )}
                </SelectContent>
              </Select>
              
              <Input name="data" placeholder="Enter JSON data" />
              
              <Button type="submit">Submit</Button>
            </form>
          </CardContent>
        </Card>
      )}

      {response && (
        <Card className="mt-4">
          <CardHeader>
            <CardTitle>Response</CardTitle>
          </CardHeader>
          <CardContent>
            <pre>{JSON.stringify(response, null, 2)}</pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
}