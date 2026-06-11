"use client";

import { Suspense } from "react";
import CreateClassContent from "./createClassContent";

export default function CreateClassPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <CreateClassContent />
    </Suspense>
  );
}