-- DropForeignKey
ALTER TABLE "profiles" DROP CONSTRAINT "profiles_id_fkey";

-- AddForeignKey
ALTER TABLE "profiles" ADD CONSTRAINT "profiles_id_fkey" FOREIGN KEY ("id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
