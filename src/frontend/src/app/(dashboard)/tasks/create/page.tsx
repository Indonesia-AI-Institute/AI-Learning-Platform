"use client";

import { Suspense } from "react";
import CreateTaskContent from "./createTaskContent";

export default function CreateTaskPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <CreateTaskContent />
    </Suspense>
  );
}