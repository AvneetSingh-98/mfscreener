import { redirect } from "next/navigation";

export default function HomePage() {
  // Redirect to Large Cap by default
  redirect("/category/large-cap");
}
